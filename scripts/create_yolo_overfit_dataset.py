from __future__ import annotations

from pathlib import Path
import argparse
import json
import shutil


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="YOLO dataset root")
    parser.add_argument("--output", required=True, help="Output overfit dataset root")
    parser.add_argument("--limit", type=int, default=32)
    args = parser.parse_args()

    source = Path(args.source)
    output = Path(args.output)
    if output.exists():
        shutil.rmtree(output)
    label_paths: list[Path] = []
    for label_path in sorted((source / "labels" / "train").glob("*.txt")):
        if label_path.read_text(encoding="utf-8").strip():
            label_paths.append(label_path)
        if len(label_paths) >= args.limit:
            break

    for split in ("train", "val"):
        (output / "images" / split).mkdir(parents=True, exist_ok=True)
        (output / "labels" / split).mkdir(parents=True, exist_ok=True)
        for label_path in label_paths:
            image_path = source / "images" / "train" / f"{label_path.stem}.jpg"
            shutil.copy2(image_path, output / "images" / split / image_path.name)
            shutil.copy2(label_path, output / "labels" / split / label_path.name)

    data_yaml = output / "data.yaml"
    data_yaml.write_text(
        "\n".join(
            [
                f"path: {output}",
                "train: images/train",
                "val: images/val",
                "names: ['balcony', 'blind']",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "dataset": str(output),
                "images": len(label_paths),
                "data_yaml": str(data_yaml),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
