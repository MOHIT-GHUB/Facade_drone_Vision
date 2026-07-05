from __future__ import annotations

from pathlib import Path
from collections import Counter
import argparse
import json
import random
import shutil
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]

YOLO_CLASSES = {
    "balcony": 0,
    "blind": 1,
}


def parse_objects(xml_path: Path) -> list[dict[str, float | str]]:
    text = xml_path.read_text(encoding="utf-8", errors="ignore")
    root = ET.fromstring(f"<root>{text}</root>")
    objects: list[dict[str, float | str]] = []
    for obj in root.findall("object"):
        name = (obj.findtext("labelname") or "").strip()
        if name not in YOLO_CLASSES:
            continue
        xs = [float(x.text) for x in obj.findall("./points/x") if x.text]
        ys = [float(y.text) for y in obj.findall("./points/y") if y.text]
        if len(xs) < 2 or len(ys) < 2:
            continue
        x0, x1 = max(0.0, min(xs)), min(1.0, max(xs))
        y0, y1 = max(0.0, min(ys)), min(1.0, max(ys))
        if x1 <= x0 or y1 <= y0:
            continue
        objects.append(
            {
                "class_name": name,
                "class_id": YOLO_CLASSES[name],
                "x_center": (x0 + x1) / 2,
                "y_center": (y0 + y1) / 2,
                "width": x1 - x0,
                "height": y1 - y0,
            }
        )
    return objects


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", default=str(ROOT / "data" / "raw" / "cmp_facade"))
    parser.add_argument("--output-dir", default=str(ROOT / "data" / "processed" / "cmp_yolo_obstacles"))
    parser.add_argument("--val-fraction", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    out_dir = Path(args.output_dir)
    rng = random.Random(args.seed)
    image_paths = sorted(raw_dir.rglob("*.jpg"))
    rng.shuffle(image_paths)

    counts: Counter[str] = Counter()
    written = {"train": 0, "val": 0}
    object_files = {"train": 0, "val": 0}
    val_count = int(len(image_paths) * args.val_fraction)

    for idx, image_path in enumerate(image_paths):
        split = "val" if idx < val_count else "train"
        xml_path = image_path.with_suffix(".xml")
        if not xml_path.exists():
            continue
        objects = parse_objects(xml_path)
        image_out_dir = out_dir / "images" / split
        label_out_dir = out_dir / "labels" / split
        image_out_dir.mkdir(parents=True, exist_ok=True)
        label_out_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(image_path, image_out_dir / image_path.name)
        label_path = label_out_dir / f"{image_path.stem}.txt"
        lines = []
        for obj in objects:
            counts[str(obj["class_name"])] += 1
            lines.append(
                f"{obj['class_id']} {obj['x_center']:.6f} {obj['y_center']:.6f} "
                f"{obj['width']:.6f} {obj['height']:.6f}"
            )
        label_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        written[split] += 1
        object_files[split] += int(bool(lines))

    data_yaml = out_dir / "data.yaml"
    names = [name for name, _ in sorted(YOLO_CLASSES.items(), key=lambda kv: kv[1])]
    data_yaml.write_text(
        "\n".join(
            [
                f"path: {out_dir}",
                "train: images/train",
                "val: images/val",
                f"names: {names}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    manifest = {
        "classes": YOLO_CLASSES,
        "counts": dict(counts),
        "images_written": written,
        "images_with_objects": object_files,
        "data_yaml": str(data_yaml),
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
