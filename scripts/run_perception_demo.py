from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from facade_uav.data.synthetic_facade import generate_synthetic_facade
from facade_uav.perception.opencv_cleaning_zone import (
    build_zone_map_from_image,
    render_zone_map,
)
from facade_uav.planning.coverage_path import plan_greedy_cleaning_path


def main() -> None:
    output_dir = ROOT / "outputs" / "perception_demo"
    output_dir.mkdir(parents=True, exist_ok=True)
    facade_path = output_dir / "synthetic_facade.png"
    zone_path = output_dir / "cleaning_zone_map.png"
    plan_path = output_dir / "cleaning_path.json"
    metrics_path = output_dir / "metrics.json"

    metadata = generate_synthetic_facade(facade_path, seed=21)
    zone_map = build_zone_map_from_image(facade_path, grid_width=12, grid_height=8)
    render_zone_map(zone_map, zone_path)
    path = plan_greedy_cleaning_path(zone_map)
    plan_path.write_text(json.dumps(path, indent=2), encoding="utf-8")
    metrics = {
        "input": str(facade_path),
        "zone_map": str(zone_path),
        "cleaning_path": str(plan_path),
        "synthetic_metadata": metadata,
        "zone_summary": zone_map.summary(),
        "path_waypoint_count": len(path),
    }
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics["zone_summary"], indent=2))
    print(f"wrote {facade_path}")
    print(f"wrote {zone_path}")
    print(f"wrote {metrics_path}")


if __name__ == "__main__":
    main()
