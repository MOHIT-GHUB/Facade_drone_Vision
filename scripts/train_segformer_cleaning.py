from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from facade_uav.perception.segformer_cleaning import (
    CLEANING_ID_TO_NAME,
    load_manifest,
    split_samples,
)


class CleaningSegmentationDataset:
    def __init__(self, samples, processor, image_size: int) -> None:
        self.samples = samples
        self.processor = processor
        self.image_size = image_size

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int):
        import torch
        from PIL import Image

        sample = self.samples[idx]
        image = Image.open(sample.image).convert("RGB").resize((self.image_size, self.image_size))
        mask = Image.open(sample.mask).resize((self.image_size, self.image_size), resample=Image.Resampling.NEAREST)
        encoded = self.processor(images=image, segmentation_maps=mask, return_tensors="pt")
        return {
            "pixel_values": encoded["pixel_values"].squeeze(0),
            "labels": encoded["labels"].squeeze(0).to(torch.long),
        }


def evaluate_pixel_accuracy(model, loader, device) -> float:
    import torch
    import torch.nn.functional as F

    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for batch in loader:
            pixel_values = batch["pixel_values"].to(device)
            labels = batch["labels"].to(device)
            outputs = model(pixel_values=pixel_values)
            logits = F.interpolate(outputs.logits, size=labels.shape[-2:], mode="bilinear", align_corners=False)
            preds = logits.argmax(dim=1)
            correct += int((preds == labels).sum().item())
            total += int(labels.numel())
    model.train()
    return correct / max(1, total)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=str(ROOT / "data" / "processed" / "cmp_cleaning" / "manifest.json"))
    parser.add_argument("--output-dir", default=str(ROOT / "models" / "segformer_cleaning"))
    parser.add_argument("--base-model", default="nvidia/mit-b0")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--limit", type=int, default=80)
    parser.add_argument("--image-size", type=int, default=256)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--learning-rate", type=float, default=5e-5)
    args = parser.parse_args()

    try:
        import torch
        from torch.utils.data import DataLoader
        from transformers import SegformerForSemanticSegmentation, SegformerImageProcessor
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Install dependencies with: python3 -m pip install --user transformers accelerate"
        ) from exc

    samples = load_manifest(args.manifest)
    train_samples, val_samples = split_samples(samples, limit=args.limit)
    processor = SegformerImageProcessor(do_reduce_labels=False, size={"height": args.image_size, "width": args.image_size})

    id2label = {idx: name for idx, name in CLEANING_ID_TO_NAME.items()}
    label2id = {name: idx for idx, name in id2label.items()}
    model = SegformerForSemanticSegmentation.from_pretrained(
        args.base_model,
        num_labels=len(id2label),
        id2label=id2label,
        label2id=label2id,
        ignore_mismatched_sizes=True,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    train_ds = CleaningSegmentationDataset(train_samples, processor, args.image_size)
    val_ds = CleaningSegmentationDataset(val_samples, processor, args.image_size)
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size)

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)
    history = []
    model.train()
    for epoch in range(args.epochs):
        total_loss = 0.0
        for step, batch in enumerate(train_loader, start=1):
            optimizer.zero_grad(set_to_none=True)
            pixel_values = batch["pixel_values"].to(device)
            labels = batch["labels"].to(device)
            outputs = model(pixel_values=pixel_values, labels=labels)
            outputs.loss.backward()
            optimizer.step()
            total_loss += float(outputs.loss.item())
            if step % 10 == 0:
                print({"epoch": epoch + 1, "step": step, "loss": round(total_loss / step, 4)})
        val_acc = evaluate_pixel_accuracy(model, val_loader, device)
        row = {
            "epoch": epoch + 1,
            "train_loss": round(total_loss / max(1, len(train_loader)), 4),
            "val_pixel_accuracy": round(val_acc, 4),
            "train_samples": len(train_ds),
            "val_samples": len(val_ds),
            "device": str(device),
        }
        history.append(row)
        print(row)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output_dir)
    processor.save_pretrained(output_dir)
    (output_dir / "training_history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
    print(json.dumps({"saved_model": str(output_dir), "history": history}, indent=2))


if __name__ == "__main__":
    main()
