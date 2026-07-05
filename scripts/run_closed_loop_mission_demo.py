from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from facade_uav.cleaning_zone_map import CleaningZoneMap
from facade_uav.integration.closed_loop import MissionExecutorConfig, execute_closed_loop_route
from facade_uav.perception.object_identification import identify_objects_from_zone_map, write_identified_objects
from facade_uav.perception.opencv_cleaning_zone import render_zone_map
from facade_uav.planning.coverage_path import (
    plan_obstacle_aware_cleaning_route,
    validate_route_clearance,
)


def build_fused_perception_demo_map() -> CleaningZoneMap:
    zone_map = CleaningZoneMap(12, 8)
    for z in range(zone_map.height):
        for x in range(zone_map.width):
            zone_map.set_surface_type(x, z, "glass")
            zone_map.set_dirty(x, z, 0.12)

    blocked_objects = [
        (9, 1, "protruding_balcony"),
        (9, 2, "protruding_balcony"),
        (9, 3, "protruding_balcony"),
        (9, 4, "protruding_balcony"),
        (9, 5, "protruding_balcony"),
        (5, 3, "maintenance_ledge"),
        (6, 3, "maintenance_ledge"),
        (7, 3, "maintenance_ledge"),
        (2, 5, "open_window"),
    ]
    for x, z, object_type in blocked_objects:
        zone_map.mark_object(x, z, object_type, 0.95, "blocked")

    caution_objects = [
        (4, 1, "blind_or_shutter"),
        (5, 1, "blind_or_shutter"),
        (6, 1, "blind_or_shutter"),
        (7, 1, "blind_or_shutter"),
        (3, 6, "thermal_moisture_anomaly"),
    ]
    for x, z, object_type in caution_objects:
        zone_map.mark_object(x, z, object_type, 0.8, "caution")

    for target in [(10, 1), (10, 2), (10, 5), (8, 6), (1, 6), (3, 2), (5, 5)]:
        zone_map.set_dirty(*target, confidence=0.9)
    return zone_map


def main() -> None:
    output_dir = ROOT / "outputs" / "closed_loop_mission"
    output_dir.mkdir(parents=True, exist_ok=True)

    zone_map = build_fused_perception_demo_map()
    objects = identify_objects_from_zone_map(zone_map)
    route = plan_obstacle_aware_cleaning_route(
        zone_map,
        start=(0, 0),
        threshold=0.25,
        clearance_cells=1,
    )
    clearance_violations = validate_route_clearance(zone_map, route, clearance_cells=1)
    nominal_result = execute_closed_loop_route(zone_map, route)

    fault_zone_map = build_fused_perception_demo_map()
    fault_route = plan_obstacle_aware_cleaning_route(
        fault_zone_map,
        start=(0, 0),
        threshold=0.25,
        clearance_cells=1,
    )
    fault_result = execute_closed_loop_route(
        fault_zone_map,
        fault_route,
        config=MissionExecutorConfig(injected_gust_step=1),
    )

    render_zone_map(zone_map, output_dir / "closed_loop_zone_map.png")
    write_identified_objects(objects, output_dir / "identified_objects.json")
    (output_dir / "route_plan.json").write_text(json.dumps(route, indent=2), encoding="utf-8")
    (output_dir / "nominal_execution.json").write_text(json.dumps(nominal_result, indent=2), encoding="utf-8")
    (output_dir / "fault_execution.json").write_text(json.dumps(fault_result, indent=2), encoding="utf-8")

    summary = {
        "zone_summary": zone_map.summary(),
        "object_summary": zone_map.object_summary(),
        "identified_object_count": len(objects),
        "route_step_count": len(route["steps"]),
        "skipped_targets": route["skipped_targets"],
        "clearance_violations": clearance_violations,
        "nominal_metrics": nominal_result["metrics"],
        "fault_metrics": fault_result["metrics"],
        "artifacts": {
            "zone_map": str((output_dir / "closed_loop_zone_map.png").resolve()),
            "objects": str((output_dir / "identified_objects.json").resolve()),
            "route": str((output_dir / "route_plan.json").resolve()),
            "nominal_execution": str((output_dir / "nominal_execution.json").resolve()),
            "fault_execution": str((output_dir / "fault_execution.json").resolve()),
        },
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))

    if clearance_violations:
        raise SystemExit("closed-loop route entered inflated obstacle clearance")
    if nominal_result["metrics"]["clean_events"] <= 0:
        raise SystemExit("closed-loop mission did not clean any target")
    if fault_result["metrics"]["safety_overrides"] <= 0:
        raise SystemExit("fault mission did not trigger safety override")


if __name__ == "__main__":
    main()
