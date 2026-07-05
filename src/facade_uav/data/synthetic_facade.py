from __future__ import annotations

import argparse
import json
from pathlib import Path
import random


def _load_dependencies():
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Synthetic facade generation requires numpy and opencv-python-headless."
        ) from exc
    return cv2, np


def generate_synthetic_facade(
    output_path: str | Path,
    width_px: int = 1280,
    height_px: int = 720,
    cols: int = 8,
    rows: int = 5,
    seed: int = 42,
) -> dict[str, object]:
    cv2, np = _load_dependencies()
    rng = random.Random(seed)
    image = np.zeros((height_px, width_px, 3), dtype=np.uint8)
    image[:] = (170, 205, 215)

    margin_x = int(width_px * 0.05)
    margin_y = int(height_px * 0.07)
    facade_w = width_px - 2 * margin_x
    facade_h = height_px - 2 * margin_y
    cell_w = facade_w // cols
    cell_h = facade_h // rows

    dirty_panels: list[dict[str, int]] = []
    thermal_anomalies: list[dict[str, int]] = []
    obstacles: list[dict[str, int]] = []
    concrete_panels: list[dict[str, int]] = []

    cv2.rectangle(
        image,
        (margin_x - 10, margin_y - 10),
        (margin_x + facade_w + 10, margin_y + facade_h + 10),
        (45, 55, 60),
        -1,
    )

    for row in range(rows):
        for col in range(cols):
            x0 = margin_x + col * cell_w + 5
            y0 = margin_y + row * cell_h + 5
            x1 = margin_x + (col + 1) * cell_w - 5
            y1 = margin_y + (row + 1) * cell_h - 5
            is_concrete = col in {0, cols - 1} or (row == rows - 1 and col in {2, 3, 4})
            if is_concrete:
                base = rng.randint(125, 155)
                tint = (base, base, base)
                concrete_panels.append({"col": col, "row": row})
            else:
                base = rng.randint(175, 225)
                tint = (base, min(255, base + 20), min(255, base + 28))
            cv2.rectangle(image, (x0, y0), (x1, y1), tint, -1)

            if not is_concrete and rng.random() < 0.34:
                cx = rng.randint(x0 + 20, x1 - 20)
                cy = rng.randint(y0 + 20, y1 - 20)
                rx = rng.randint(20, max(22, cell_w // 4))
                ry = rng.randint(12, max(14, cell_h // 4))
                dirt_color = rng.choice([(80, 95, 90), (95, 105, 100), (70, 85, 82)])
                cv2.ellipse(image, (cx, cy), (rx, ry), rng.randint(0, 180), 0, 360, dirt_color, -1)
                dirty_panels.append({"col": col, "row": row})

            if not is_concrete and rng.random() < 0.09:
                ax = rng.randint(x0 + 25, x1 - 25)
                ay = rng.randint(y0 + 25, y1 - 25)
                cv2.circle(image, (ax, ay), rng.randint(10, 18), (45, 65, 180), -1)
                thermal_anomalies.append({"col": col, "row": row})

    for col in range(cols + 1):
        x = margin_x + col * cell_w
        cv2.rectangle(image, (x - 4, margin_y), (x + 4, margin_y + facade_h), (35, 40, 45), -1)

    for row in range(rows + 1):
        y = margin_y + row * cell_h
        cv2.rectangle(image, (margin_x, y - 4), (margin_x + facade_w, y + 4), (35, 40, 45), -1)

    for _ in range(4):
        col = rng.randrange(cols)
        row = rng.randrange(rows)
        x0 = margin_x + col * cell_w + cell_w // 3
        y0 = margin_y + row * cell_h + cell_h // 3
        x1 = x0 + cell_w // 3
        y1 = y0 + cell_h // 4
        cv2.rectangle(image, (x0, y0), (x1, y1), (55, 55, 58), -1)
        cv2.rectangle(image, (x0 + 6, y0 + 6), (x1 - 6, y1 - 6), (110, 115, 120), 2)
        obstacles.append({"col": col, "row": row})

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), image)

    metadata = {
        "image": str(output_path),
        "width_px": width_px,
        "height_px": height_px,
        "cols": cols,
        "rows": rows,
        "dirty_panels": dirty_panels,
        "concrete_panels": concrete_panels,
        "thermal_anomalies": thermal_anomalies,
        "obstacles": obstacles,
    }
    output_path.with_suffix(".json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="outputs/synthetic_facade.png")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    metadata = generate_synthetic_facade(args.output, seed=args.seed)
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
