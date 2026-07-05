from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from facade_uav.cleaning_zone_map import CleaningZoneMap
from facade_uav.perception.object_identification import identify_objects_from_zone_map, write_identified_objects
from facade_uav.planning.coverage_path import plan_obstacle_aware_cleaning_route
from facade_uav.perception.opencv_cleaning_zone import render_zone_map


def build_demo_map() -> CleaningZoneMap:
    zone_map = CleaningZoneMap(12, 8)
    for z in range(zone_map.height):
        for x in range(zone_map.width):
            zone_map.set_surface_type(x, z, "glass")
            zone_map.set_dirty(x, z, 0.15)

    for x, z in [(9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (5, 3), (6, 3), (7, 3), (2, 5)]:
        zone_map.mark_object(x, z, "protruding_balcony", 0.95, "blocked")

    for x, z in [(4, 1), (5, 1), (6, 1), (7, 1), (3, 6)]:
        zone_map.mark_object(x, z, "blind_or_shutter", 0.8, "caution")

    for target in [(10, 1), (10, 2), (10, 5), (8, 6), (1, 6), (3, 2), (5, 5)]:
        zone_map.set_dirty(*target, confidence=0.9)
    return zone_map


def render_route(zone_map: CleaningZoneMap, route: dict[str, object], output_path: Path, scale: int = 44) -> None:
    import cv2
    import numpy as np

    image = np.full((zone_map.height * scale, zone_map.width * scale, 3), 245, dtype=np.uint8)
    for z in range(zone_map.height):
        for x in range(zone_map.width):
            cell = zone_map.cell(x, z)
            if cell.risk_level == "blocked":
                color = (45, 45, 45)
            elif cell.risk_level == "caution":
                color = (0, 190, 230)
            elif cell.surface_type == "glass":
                color = (90, 245, 90)
            else:
                color = (150, 150, 150)
            x0, y0 = x * scale, z * scale
            cv2.rectangle(image, (x0, y0), (x0 + scale - 1, y0 + scale - 1), color, -1)
            cv2.rectangle(image, (x0, y0), (x0 + scale - 1, y0 + scale - 1), (90, 90, 90), 1)

    steps = route["steps"]
    points = []
    for step in steps:
        if not isinstance(step, dict):
            continue
        points.append((int(step["x"]) * scale + scale // 2, int(step["z"]) * scale + scale // 2))
        if step.get("action") == "clean":
            cv2.circle(image, points[-1], scale // 4, (255, 255, 255), -1)
            cv2.circle(image, points[-1], scale // 4, (40, 70, 255), 2)
    for a, b in zip(points, points[1:]):
        cv2.line(image, a, b, (255, 40, 40), 3)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), image)


def main() -> None:
    output_dir = ROOT / "outputs" / "object_avoidance_demo"
    output_dir.mkdir(parents=True, exist_ok=True)
    zone_map = build_demo_map()
    objects = identify_objects_from_zone_map(zone_map)
    route = plan_obstacle_aware_cleaning_route(zone_map, start=(0, 0), threshold=0.25, clearance_cells=1)

    render_zone_map(zone_map, output_dir / "zone_map.png")
    render_route(zone_map, route, output_dir / "avoidance_route.png")
    write_identified_objects(objects, output_dir / "identified_objects.json")
    (output_dir / "route_plan.json").write_text(json.dumps(route, indent=2), encoding="utf-8")

    blocked = zone_map.blocked_cells(clearance_cells=1)
    violations = [
        step for step in route["steps"]
        if isinstance(step, dict) and (int(step["x"]), int(step["z"])) in blocked and step.get("action") != "clean"
    ]
    summary = {
        "identified_object_count": len(objects),
        "object_summary": zone_map.object_summary(),
        "route_step_count": len(route["steps"]),
        "skipped_targets": route["skipped_targets"],
        "clearance_violations": len(violations),
        "route_plan": str((output_dir / "route_plan.json").resolve()),
        "avoidance_route": str((output_dir / "avoidance_route.png").resolve()),
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
