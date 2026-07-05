from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from facade_uav.cleaning_zone_map import CleaningZoneMap
from facade_uav.perception.yolo_obstacles import ObstacleDetection


@dataclass(frozen=True)
class IdentifiedObject:
    object_type: str
    risk_level: str
    confidence: float
    cells: list[tuple[int, int]]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["cells"] = [{"x": x, "z": z} for x, z in self.cells]
        return data


DETECTION_RISK = {
    "balcony": "blocked",
    "blind": "caution",
    "frame": "blocked",
    "thermal_anomaly": "caution",
}


def identify_objects_from_zone_map(zone_map: CleaningZoneMap) -> list[IdentifiedObject]:
    objects: list[IdentifiedObject] = []
    for z in range(zone_map.height):
        for x in range(zone_map.width):
            cell = zone_map.cell(x, z)
            if cell.object_type == "none" and not cell.obstacle and not cell.thermal_anomaly:
                continue
            object_type = cell.object_type
            if object_type == "none":
                object_type = "frame" if cell.obstacle else "thermal_anomaly"
            risk_level = cell.risk_level
            if risk_level == "clear":
                risk_level = DETECTION_RISK.get(object_type, "caution")
            objects.append(
                IdentifiedObject(
                    object_type=object_type,
                    risk_level=risk_level,
                    confidence=cell.object_confidence or 1.0,
                    cells=[(x, z)],
                    reason="zone_map_cell_state",
                )
            )
    return objects


def apply_yolo_detections_to_zone_map(
    zone_map: CleaningZoneMap,
    detections: list[ObstacleDetection],
    image_width: int,
    image_height: int,
    min_confidence: float = 0.25,
) -> list[IdentifiedObject]:
    """Project detector boxes into the planning grid.

    Current YOLO weights are not trusted yet, so callers should use a real
    confidence threshold. Low-confidence detections must stay diagnostic only.
    """

    identified: list[IdentifiedObject] = []
    cell_w = max(1.0, image_width / zone_map.width)
    cell_h = max(1.0, image_height / zone_map.height)
    for detection in detections:
        if detection.confidence < min_confidence:
            continue
        x0, y0, x1, y1 = detection.xyxy
        gx0 = max(0, min(zone_map.width - 1, int(x0 / cell_w)))
        gx1 = max(0, min(zone_map.width - 1, int(x1 / cell_w)))
        gz0 = max(0, min(zone_map.height - 1, int(y0 / cell_h)))
        gz1 = max(0, min(zone_map.height - 1, int(y1 / cell_h)))
        cells: list[tuple[int, int]] = []
        risk = DETECTION_RISK.get(detection.class_name, "blocked")
        for z in range(gz0, gz1 + 1):
            for x in range(gx0, gx1 + 1):
                zone_map.mark_object(x, z, detection.class_name, detection.confidence, risk)
                cells.append((x, z))
        identified.append(
            IdentifiedObject(
                object_type=detection.class_name,
                risk_level=risk,
                confidence=detection.confidence,
                cells=cells,
                reason="yolo_box_projection",
            )
        )
    return identified


def write_identified_objects(objects: list[IdentifiedObject], output_path: str | Path) -> None:
    import json

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(
        json.dumps([obj.to_dict() for obj in objects], indent=2),
        encoding="utf-8",
    )
