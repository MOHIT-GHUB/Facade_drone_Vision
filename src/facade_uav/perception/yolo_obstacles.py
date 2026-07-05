from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ObstacleDetection:
    class_id: int
    class_name: str
    confidence: float
    xyxy: tuple[float, float, float, float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def detect_obstacles(
    model_path: str | Path,
    image_path: str | Path,
    confidence: float = 0.25,
    image_size: int = 640,
    device: str = "cpu",
) -> list[ObstacleDetection]:
    """Run a YOLO obstacle detector on one facade image."""

    try:
        from ultralytics import YOLO
    except ModuleNotFoundError as exc:
        raise RuntimeError("Ultralytics is required for YOLO obstacle inference.") from exc

    model = YOLO(str(model_path))
    results = model.predict(
        source=str(image_path),
        conf=confidence,
        imgsz=image_size,
        device=device,
        verbose=False,
    )
    if not results:
        return []

    result = results[0]
    names = result.names or {}
    detections: list[ObstacleDetection] = []
    for box in result.boxes:
        class_id = int(box.cls.item())
        xyxy = tuple(float(v) for v in box.xyxy[0].tolist())
        detections.append(
            ObstacleDetection(
                class_id=class_id,
                class_name=str(names.get(class_id, class_id)),
                confidence=float(box.conf.item()),
                xyxy=xyxy,  # pixel coordinates: x0, y0, x1, y1
            )
        )
    return detections


def render_obstacle_overlay(
    image_path: str | Path,
    detections: list[ObstacleDetection],
    output_path: str | Path,
) -> None:
    try:
        import cv2  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError("OpenCV is required to render obstacle overlays.") from exc

    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"could not read image: {image_path}")

    palette = {
        "balcony": (60, 180, 255),
        "blind": (255, 90, 90),
    }
    for detection in detections:
        x0, y0, x1, y1 = [int(round(v)) for v in detection.xyxy]
        color = palette.get(detection.class_name, (90, 255, 120))
        cv2.rectangle(image, (x0, y0), (x1, y1), color, 2)
        label = f"{detection.class_name} {detection.confidence:.2f}"
        cv2.putText(
            image,
            label,
            (x0, max(14, y0 - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            color,
            1,
            cv2.LINE_AA,
        )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), image)
