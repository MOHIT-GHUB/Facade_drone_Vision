from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from facade_uav.perception.opencv_cleaning_zone import render_zone_map
from facade_uav.perception.segformer_cleaning import cleaning_mask_to_zone_map, colorize_mask
from facade_uav.planning.coverage_path import plan_greedy_cleaning_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", default=str(ROOT / "models" / "segformer_cleaning"))
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", default=str(ROOT / "outputs" / "segformer_building_analysis"))
    parser.add_argument("--grid-width", type=int, default=12)
    parser.add_argument("--grid-height", type=int, default=8)
    args = parser.parse_args()

    try:
        import torch
        import torch.nn.functional as F
        from PIL import Image
        from transformers import SegformerForSemanticSegmentation, SegformerImageProcessor
    except ModuleNotFoundError as exc:
        raise RuntimeError("Install transformers, torch, torchvision, and Pillow first.") from exc

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
    color_mask = colorize_mask(mask)
    overlay = Image.blend(image, color_mask, 0.45)
    zone_map = cleaning_mask_to_zone_map(mask, args.input, args.grid_width, args.grid_height)
    path = plan_greedy_cleaning_path(zone_map)

    mask_path = output_dir / "segformer_cleaning_mask.png"
    overlay_path = output_dir / "segformer_overlay.png"
    zone_path = output_dir / "cleaning_zone_map.png"
    path_path = output_dir / "cleaning_path.json"
    summary_path = output_dir / "summary.json"
    mask.save(mask_path)
    overlay.save(overlay_path)
    render_zone_map(zone_map, zone_path)
    path_path.write_text(json.dumps(path, indent=2), encoding="utf-8")
    summary = {
        "input": str(Path(args.input).resolve()),
        "model_dir": str(Path(args.model_dir).resolve()),
        "segformer_mask": str(mask_path.resolve()),
        "segformer_overlay": str(overlay_path.resolve()),
        "zone_map": str(zone_path.resolve()),
        "cleaning_path": str(path_path.resolve()),
        "summary": zone_map.summary(),
        "path_waypoint_count": len(path),
        "device": str(device),
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
