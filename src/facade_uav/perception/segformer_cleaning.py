from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import random

from facade_uav.cleaning_zone_map import CleaningZoneMap


CLEANING_ID_TO_NAME = {
    0: "skip_background",
    1: "cleanable_glass",
    2: "skip_structure",
    3: "skip_obstacle",
    4: "conditional_glass",
}

CLEANING_COLORS = {
    0: (30, 30, 30),
    1: (70, 230, 255),
    2: (150, 150, 150),
    3: (230, 80, 80),
    4: (80, 180, 230),
}


@dataclass(frozen=True)
class SegFormerSample:
    image: str
    mask: str


def load_manifest(manifest_path: str | Path) -> list[SegFormerSample]:
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    return [SegFormerSample(image=s["image"], mask=s["mask"]) for s in manifest["samples"]]


def split_samples(
    samples: list[SegFormerSample],
    val_fraction: float = 0.15,
    seed: int = 42,
    limit: int = 0,
) -> tuple[list[SegFormerSample], list[SegFormerSample]]:
    shuffled = list(samples)
    random.Random(seed).shuffle(shuffled)
    if limit:
        shuffled = shuffled[:limit]
    val_count = max(1, int(len(shuffled) * val_fraction))
    return shuffled[val_count:], shuffled[:val_count]


def colorize_mask(mask):
    try:
        import numpy as np
        from PIL import Image
    except ModuleNotFoundError as exc:
        raise RuntimeError("NumPy and Pillow are required to colorize masks.") from exc

    arr = np.asarray(mask, dtype=np.uint8)
    color = np.zeros((arr.shape[0], arr.shape[1], 3), dtype=np.uint8)
    for idx, rgb in CLEANING_COLORS.items():
        color[arr == idx] = rgb
    return Image.fromarray(color)


def surface_type_from_cleaning_id(cleaning_id: int) -> tuple[str, bool]:
    if cleaning_id == 1:
        return "glass", False
    if cleaning_id == 4:
        return "glass", False
    if cleaning_id == 2:
        return "concrete", False
    if cleaning_id == 3:
        return "frame", True
    return "unknown", False


def cleaning_mask_to_zone_map(
    mask,
    source_image_path: str | Path,
    grid_width: int = 12,
    grid_height: int = 8,
) -> CleaningZoneMap:
    """Convert a pixel cleaning mask into the planning grid.

    SegFormer predicts clean/skip material classes. Dirt confidence is still
    estimated from the RGB image inside cells that are cleanable glass.
    """

    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError("OpenCV and NumPy are required to build a zone map.") from exc

    arr = np.asarray(mask, dtype=np.uint8)
    image = cv2.imread(str(source_image_path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"could not read image: {source_image_path}")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    arr_h, arr_w = arr.shape[:2]
    img_h, img_w = gray.shape[:2]
    if (arr_w, arr_h) != (img_w, img_h):
        arr = cv2.resize(arr, (img_w, img_h), interpolation=cv2.INTER_NEAREST)
        arr_h, arr_w = arr.shape[:2]

    zone_map = CleaningZoneMap(grid_width, grid_height)
    cell_w = max(1, arr_w // grid_width)
    cell_h = max(1, arr_h // grid_height)

    for z in range(grid_height):
        for x in range(grid_width):
            x0 = x * cell_w
            y0 = z * cell_h
            x1 = arr_w if x == grid_width - 1 else (x + 1) * cell_w
            y1 = arr_h if z == grid_height - 1 else (z + 1) * cell_h
            mask_patch = arr[y0:y1, x0:x1]
            gray_patch = gray[y0:y1, x0:x1]
            ids, counts = np.unique(mask_patch, return_counts=True)
            majority_id = int(ids[int(np.argmax(counts))])
            surface_type, obstacle = surface_type_from_cleaning_id(majority_id)
            zone_map.set_surface_type(x, z, surface_type)
            zone_map.set_obstacle(x, z, obstacle)
            if surface_type == "glass":
                darkness = 1.0 - float(np.mean(gray_patch)) / 255.0
                texture = float(np.std(gray_patch)) / 96.0
                dirty_conf = max(0.0, min(1.0, 1.15 * darkness + 0.65 * texture))
            else:
                dirty_conf = 0.0
            zone_map.set_dirty(x, z, dirty_conf)

    return zone_map
