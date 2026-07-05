from __future__ import annotations

from pathlib import Path
import argparse
import json


ROOT = Path(__file__).resolve().parents[1]

# Cleaning mask IDs for our UAV decision layer.
# 0 background/skip, 1 cleanable glass candidate, 2 structural skip,
# 3 obstacle skip, 4 conditional glass candidate.
CLEANING_ID_TO_NAME = {
    0: "skip_background",
    1: "cleanable_glass",
    2: "skip_structure",
    3: "skip_obstacle",
    4: "conditional_glass",
}

# CMP palette IDs observed in masks:
# 1 background, 2 facade, 3 window, 4 door, 5 cornice, 6 sill,
# 7 balcony, 8 blind, 9 deco, 10 molding, 11 pillar, 12 shop.
CMP_TO_CLEANING = {
    1: 0,
    2: 2,
    3: 1,
    4: 4,
    5: 2,
    6: 2,
    7: 3,
    8: 3,
    9: 2,
    10: 2,
    11: 2,
    12: 4,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--index",
        default=str(ROOT / "data" / "processed" / "cmp_facade_index.json"),
    )
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "data" / "processed" / "cmp_cleaning"),
    )
    parser.add_argument("--limit", type=int, default=0, help="0 converts all samples")
    args = parser.parse_args()

    try:
        from PIL import Image
        import numpy as np
    except ModuleNotFoundError as exc:
        raise RuntimeError("Pillow and NumPy are required.") from exc

    index = json.loads(Path(args.index).read_text(encoding="utf-8"))
    out_dir = Path(args.output_dir)
    image_dir = out_dir / "images"
    mask_dir = out_dir / "masks"
    image_dir.mkdir(parents=True, exist_ok=True)
    mask_dir.mkdir(parents=True, exist_ok=True)

    samples = index["samples"]
    if args.limit:
        samples = samples[: args.limit]

    converted = []
    for sample in samples:
        image_path = Path(sample["image"])
        cmp_mask_path = Path(sample["mask"])
        stem = image_path.stem

        image_out = image_dir / f"{stem}.jpg"
        mask_out = mask_dir / f"{stem}.png"
        if not image_out.exists():
            Image.open(image_path).convert("RGB").save(image_out)

        cmp_mask = np.array(Image.open(cmp_mask_path))
        cleaning_mask = np.zeros_like(cmp_mask, dtype=np.uint8)
        for cmp_id, cleaning_id in CMP_TO_CLEANING.items():
            cleaning_mask[cmp_mask == cmp_id] = cleaning_id
        Image.fromarray(cleaning_mask, mode="L").save(mask_out)

        converted.append(
            {
                "image": str(image_out),
                "mask": str(mask_out),
                "source_image": str(image_path),
                "source_mask": str(cmp_mask_path),
            }
        )

    manifest = {
        "source_dataset": "CMP Facade Database",
        "sample_count": len(converted),
        "cleaning_id_to_name": CLEANING_ID_TO_NAME,
        "cmp_to_cleaning": CMP_TO_CLEANING,
        "samples": converted,
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "sample_count": len(converted),
                "output_dir": str(out_dir),
                "manifest": str(manifest_path),
                "cleaning_id_to_name": CLEANING_ID_TO_NAME,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
