from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from facade_uav.perception.opencv_cleaning_zone import build_zone_map_from_image, render_zone_map
from facade_uav.perception.object_identification import identify_objects_from_zone_map, write_identified_objects
from facade_uav.planning.coverage_path import plan_greedy_cleaning_path, plan_obstacle_aware_cleaning_route


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Building/facade image path")
    parser.add_argument("--output-dir", default="outputs/building_analysis")
    parser.add_argument("--grid-width", type=int, default=12)
    parser.add_argument("--grid-height", type=int, default=8)
    parser.add_argument(
        "--clearance-cells",
        type=int,
        default=0,
        help="Inflated obstacle clearance in grid cells. Use 1+ for denser grids.",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    zone_map = build_zone_map_from_image(args.input, args.grid_width, args.grid_height)
    overlay_path = output_dir / "cleaning_zone_map.png"
    plan_path = output_dir / "cleaning_path.json"
    route_path = output_dir / "avoidance_route.json"
    objects_path = output_dir / "identified_objects.json"
    summary_path = output_dir / "summary.json"

    render_zone_map(zone_map, overlay_path)
    path = plan_greedy_cleaning_path(zone_map)
    route = plan_obstacle_aware_cleaning_route(zone_map, clearance_cells=args.clearance_cells)
    objects = identify_objects_from_zone_map(zone_map)
    summary = {
        "input": str(Path(args.input).resolve()),
        "zone_map": str(overlay_path.resolve()),
        "cleaning_path": str(plan_path.resolve()),
        "avoidance_route": str(route_path.resolve()),
        "identified_objects": str(objects_path.resolve()),
        "summary": zone_map.summary(),
        "object_summary": zone_map.object_summary(),
        "path_waypoint_count": len(path),
        "route_step_count": len(route["steps"]),
        "skipped_targets": route["skipped_targets"],
        "clearance_cells": args.clearance_cells,
        "policy": "greedy_nearest_dirty_cleanable_glass_only",
        "route_policy": route["policy"],
    }
    plan_path.write_text(json.dumps(path, indent=2), encoding="utf-8")
    route_path.write_text(json.dumps(route, indent=2), encoding="utf-8")
    write_identified_objects(objects, objects_path)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
