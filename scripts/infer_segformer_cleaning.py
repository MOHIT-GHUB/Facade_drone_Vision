from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from facade_uav.perception.segformer_cleaning import colorize_mask


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", default=str(ROOT / "models" / "segformer_cleaning"))
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", default=str(ROOT / "outputs" / "segformer_inference"))
    args = parser.parse_args()

    try:
        import torch
        import torch.nn.functional as F
        from PIL import Image
        from transformers import SegformerForSemanticSegmentation, SegformerImageProcessor
    except ModuleNotFoundError as exc:
        raise RuntimeError("Install dependencies with: python3 -m pip install --user transformers accelerate") from exc

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    image = Image.open(args.input).convert("RGB")
    processor = SegformerImageProcessor.from_pretrained(args.model_dir)
    model = SegformerForSemanticSegmentation.from_pretrained(args.model_dir)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    encoded = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model(pixel_values=encoded["pixel_values"].to(device))
        logits = F.interpolate(outputs.logits, size=image.size[::-1], mode="bilinear", align_corners=False)
        pred = logits.argmax(dim=1)[0].cpu().numpy().astype("uint8")

    mask = Image.fromarray(pred, mode="L")
    color = colorize_mask(mask)
    overlay = Image.blend(image, color, 0.45)

    mask_path = output_dir / "predicted_cleaning_mask.png"
    overlay_path = output_dir / "predicted_cleaning_overlay.png"
    mask.save(mask_path)
    overlay.save(overlay_path)
    print(json.dumps({"mask": str(mask_path), "overlay": str(overlay_path), "device": str(device)}, indent=2))


if __name__ == "__main__":
    main()
