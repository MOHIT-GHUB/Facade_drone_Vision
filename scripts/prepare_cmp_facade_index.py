from __future__ import annotations

from pathlib import Path
from collections import Counter
import argparse
import json
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]

LABEL_ID_TO_NAME = {
    1: "background",
    2: "facade",
    3: "window",
    4: "door",
    5: "cornice",
    6: "sill",
    7: "balcony",
    8: "blind",
    9: "deco",
    10: "molding",
    11: "pillar",
    12: "shop",
}

CLEANING_CLASS_MAP = {
    "background": "skip_background",
    "facade": "skip_wall_or_unknown",
    "window": "cleanable_glass_candidate",
    "door": "conditional_glass_candidate",
    "cornice": "skip_frame_detail",
    "sill": "skip_frame_detail",
    "balcony": "skip_obstacle",
    "blind": "skip_obstacle",
    "deco": "skip_frame_detail",
    "molding": "skip_frame_detail",
    "pillar": "skip_structure",
}


def parse_xml_labels(path: Path) -> Counter[str]:
    labels: Counter[str] = Counter()
    text = path.read_text(encoding="utf-8", errors="ignore")
    wrapped = f"<root>{text}</root>"
    root = ET.fromstring(wrapped)
    for obj in root.findall("object"):
        name = obj.findtext("labelname")
        if name:
            labels[name.strip()] += 1
    return labels


def build_index(dataset_dir: Path) -> dict[str, object]:
    samples: list[dict[str, object]] = []
    object_counts: Counter[str] = Counter()
    mask_label_counts: Counter[int] = Counter()

    for jpg in sorted(dataset_dir.rglob("*.jpg")):
        mask = jpg.with_suffix(".png")
        xml = jpg.with_suffix(".xml")
        if not mask.exists() or not xml.exists():
            continue
        labels = parse_xml_labels(xml)
        object_counts.update(labels)
        samples.append(
            {
                "image": str(jpg),
                "mask": str(mask),
                "xml": str(xml),
                "split": "extended" if "/extended/" in str(jpg).replace("\\", "/") else "base",
                "object_labels": dict(labels),
            }
        )

    try:
        from PIL import Image
        import numpy as np

        for sample in samples:
            arr = np.array(Image.open(sample["mask"]))
            for value in np.unique(arr):
                mask_label_counts[int(value)] += 1
    except ModuleNotFoundError:
        pass

    return {
        "dataset": "CMP Facade Database",
        "sample_count": len(samples),
        "label_id_to_name": LABEL_ID_TO_NAME,
        "cleaning_class_map": CLEANING_CLASS_MAP,
        "object_counts": dict(object_counts),
        "mask_label_presence_counts": {
            LABEL_ID_TO_NAME.get(k, str(k)): v for k, v in sorted(mask_label_counts.items())
        },
        "samples": samples,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset-dir",
        default=str(ROOT / "data" / "raw" / "cmp_facade"),
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "data" / "processed" / "cmp_facade_index.json"),
    )
    args = parser.parse_args()

    index = build_index(Path(args.dataset_dir))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "sample_count": index["sample_count"],
                "object_counts": index["object_counts"],
                "mask_label_presence_counts": index["mask_label_presence_counts"],
                "output": str(output),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
