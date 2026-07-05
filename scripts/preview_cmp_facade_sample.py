from __future__ import annotations

from pathlib import Path
import argparse
import json


ROOT = Path(__file__).resolve().parents[1]

COLORS = {
    1: (40, 40, 40),
    2: (130, 130, 130),
    3: (70, 220, 255),
    4: (80, 180, 220),
    5: (240, 180, 80),
    6: (220, 220, 80),
    7: (220, 80, 80),
    8: (160, 80, 220),
    9: (80, 220, 120),
    10: (255, 120, 180),
    11: (180, 120, 80),
    12: (70, 160, 240),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--index",
        default=str(ROOT / "data" / "processed" / "cmp_facade_index.json"),
    )
    parser.add_argument("--sample", type=int, default=0)
    parser.add_argument(
        "--output",
        default=str(ROOT / "outputs" / "cmp_facade_preview.png"),
    )
    args = parser.parse_args()

    try:
        from PIL import Image
        import numpy as np
    except ModuleNotFoundError as exc:
        raise RuntimeError("Install Pillow and NumPy before previewing CMP samples.") from exc

    index = json.loads(Path(args.index).read_text(encoding="utf-8"))
    sample = index["samples"][args.sample]
    image = Image.open(sample["image"]).convert("RGB")
    mask = np.array(Image.open(sample["mask"]))
    color = np.zeros((mask.shape[0], mask.shape[1], 3), dtype=np.uint8)
    for label_id, rgb in COLORS.items():
        color[mask == label_id] = rgb
    overlay = Image.blend(image, Image.fromarray(color), 0.45)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    overlay.save(output)
    print(json.dumps({"sample": sample, "preview": str(output)}, indent=2))


if __name__ == "__main__":
    main()
