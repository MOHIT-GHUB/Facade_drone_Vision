from pathlib import Path
import argparse
from collections import Counter
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from facade_uav.perception.yolo_obstacles import detect_obstacles, render_obstacle_overlay


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="YOLO .pt model path")
    parser.add_argument("--input", required=True, help="Facade image path")
    parser.add_argument("--output-dir", default="outputs/yolo_obstacles")
    parser.add_argument("--confidence", type=float, default=0.25)
    parser.add_argument("--image-size", type=int, default=640)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    detections = detect_obstacles(
        model_path=args.model,
        image_path=args.input,
        confidence=args.confidence,
        image_size=args.image_size,
        device=args.device,
    )
    overlay_path = output_dir / "obstacle_overlay.png"
    detections_path = output_dir / "detections.json"
    summary = {
        "input": str(Path(args.input).resolve()),
        "model": str(Path(args.model).resolve()),
        "confidence": args.confidence,
        "detections": [d.to_dict() for d in detections],
        "overlay": str(overlay_path.resolve()),
    }
    render_obstacle_overlay(args.input, detections, overlay_path)
    detections_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    counts = Counter(d.class_name for d in detections)
    print(
        json.dumps(
            {
                "input": summary["input"],
                "model": summary["model"],
                "confidence": args.confidence,
                "detection_count": len(detections),
                "counts": dict(sorted(counts.items())),
                "detections_json": str(detections_path.resolve()),
                "overlay": str(overlay_path.resolve()),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
