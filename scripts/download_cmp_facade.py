from __future__ import annotations

from pathlib import Path
import argparse
import json
import urllib.request
import zipfile


ROOT = Path(__file__).resolve().parents[1]

DATASET_URLS = {
    "base": "https://cmp.felk.cvut.cz/~tylecr1/facade/CMP_facade_DB_base.zip",
    "extended": "https://cmp.felk.cvut.cz/~tylecr1/facade/CMP_facade_DB_extended.zip",
    "report": "https://cmp.felk.cvut.cz/~tylecr1/facade/CMP_facade_DB_2013.pdf",
}

CMP_CLASSES = [
    "facade",
    "molding",
    "cornice",
    "pillar",
    "window",
    "door",
    "sill",
    "blind",
    "balcony",
    "shop",
    "deco",
    "background",
]

CLEANING_CLASS_MAP = {
    "facade": "skip_wall_or_unknown",
    "molding": "skip_frame_detail",
    "cornice": "skip_frame_detail",
    "pillar": "skip_structure",
    "window": "cleanable_glass_candidate",
    "door": "conditional_glass_candidate",
    "sill": "skip_frame_detail",
    "blind": "skip_obstacle",
    "balcony": "skip_obstacle",
    "shop": "conditional_glass_candidate",
    "deco": "skip_frame_detail",
    "background": "skip_background",
}


def download(url: str, destination: Path) -> None:
    if destination.exists() and destination.stat().st_size > 0:
        print(f"exists {destination}")
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    print(f"downloading {url}")
    urllib.request.urlretrieve(url, destination)
    print(f"wrote {destination}")


def extract(zip_path: Path, extract_dir: Path) -> None:
    marker = extract_dir / ".extracted"
    if marker.exists():
        print(f"already extracted {zip_path.name}")
        return
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(extract_dir)
    marker.write_text("ok\n", encoding="utf-8")
    print(f"extracted {zip_path} -> {extract_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(ROOT / "data" / "raw" / "cmp_facade"))
    parser.add_argument("--skip-extended", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    selected = ["base", "report"]
    if not args.skip_extended:
        selected.insert(1, "extended")

    for key in selected:
        url = DATASET_URLS[key]
        filename = url.rsplit("/", 1)[-1]
        destination = output_dir / filename
        download(url, destination)
        if destination.suffix == ".zip":
            extract(destination, output_dir / destination.stem)

    manifest = {
        "name": "CMP Facade Database",
        "source": "https://cmp.felk.cvut.cz/~tylecr1/facade/",
        "classes": CMP_CLASSES,
        "cleaning_class_map": CLEANING_CLASS_MAP,
        "files": {key: DATASET_URLS[key] for key in selected},
    }
    (output_dir / "dataset_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
