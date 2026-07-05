from __future__ import annotations

import argparse
from pathlib import Path

from facade_uav.cleaning_zone_map import CleaningZoneMap


def _load_cv2():
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "OpenCV perception requires numpy and opencv-python. "
            "Install them with: python -m pip install -r requirements.txt"
        ) from exc
    return cv2, np


def build_zone_map_from_image(
    image_path: str | Path,
    grid_width: int = 12,
    grid_height: int = 8,
) -> CleaningZoneMap:
    """Build a deterministic cleaning-zone map from an RGB facade image.

    This is the v1 OpenCV baseline. It estimates dirt by local darkness and
    texture, then marks strong straight-line regions as likely frame obstacles.
    Learned YOLO/SegFormer/MiDaS backends can later replace these heuristics
    while preserving the same CleaningZoneMap output.
    """

    cv2, np = _load_cv2()
    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"could not read image: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 60, 140)

    h, w = gray.shape[:2]
    zone_map = CleaningZoneMap(grid_width, grid_height)
    cell_w = max(1, w // grid_width)
    cell_h = max(1, h // grid_height)

    for z in range(grid_height):
        for x in range(grid_width):
            x0 = x * cell_w
            y0 = z * cell_h
            x1 = w if x == grid_width - 1 else (x + 1) * cell_w
            y1 = h if z == grid_height - 1 else (z + 1) * cell_h
            patch = gray[y0:y1, x0:x1]
            color_patch = image[y0:y1, x0:x1]
            hsv_patch = hsv[y0:y1, x0:x1]
            edge_patch = edges[y0:y1, x0:x1]

            darkness = 1.0 - float(np.mean(patch)) / 255.0
            texture = float(np.std(patch)) / 96.0
            edge_density = float(np.mean(edge_patch > 0))
            saturation = float(np.mean(hsv_patch[:, :, 1])) / 255.0
            blue_green_bias = float(np.mean(color_patch[:, :, 0]) - np.mean(color_patch[:, :, 2])) / 255.0
            obstacle = edge_density > 0.035

            if obstacle:
                surface_type = "frame"
            elif saturation < 0.12 and float(np.mean(patch)) < 175:
                surface_type = "concrete"
            elif saturation > 0.08 or blue_green_bias > 0.03:
                surface_type = "glass"
            else:
                surface_type = "unknown"

            if surface_type == "glass":
                dirty_conf = max(0.0, min(1.0, 1.15 * darkness + 0.65 * texture))
            else:
                dirty_conf = 0.0

            zone_map.set_surface_type(x, z, surface_type)
            zone_map.set_dirty(x, z, dirty_conf)

    return zone_map


def render_zone_map(zone_map: CleaningZoneMap, output_path: str | Path, scale: int = 40) -> None:
    cv2, np = _load_cv2()
    image = np.zeros((zone_map.height * scale, zone_map.width * scale, 3), dtype=np.uint8)

    for z in range(zone_map.height):
        for x in range(zone_map.width):
            cell = zone_map.cell(x, z)
            if cell.surface_type == "frame":
                color = (30, 30, 30)
            elif cell.surface_type == "concrete":
                color = (135, 135, 135)
            elif cell.surface_type == "unknown":
                color = (80, 80, 160)
            else:
                intensity = int(255 * (1.0 - cell.dirty_confidence))
                color = (intensity, 255, intensity)
            x0 = x * scale
            y0 = z * scale
            cv2.rectangle(image, (x0, y0), (x0 + scale - 1, y0 + scale - 1), color, -1)
            cv2.rectangle(image, (x0, y0), (x0 + scale - 1, y0 + scale - 1), (80, 80, 80), 1)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), image)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--grid-width", type=int, default=12)
    parser.add_argument("--grid-height", type=int, default=8)
    args = parser.parse_args()

    zone_map = build_zone_map_from_image(args.input, args.grid_width, args.grid_height)
    render_zone_map(zone_map, args.output)
    print(zone_map.summary())


if __name__ == "__main__":
    main()
