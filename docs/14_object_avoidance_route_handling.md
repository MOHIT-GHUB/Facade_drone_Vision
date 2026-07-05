# Object Avoidance And Route Handling

Generated on 2026-07-05.

## Why This Was Added

The project needed more than object boxes on an image. A UAV can only act safely if object identification changes the route. This work connects identified facade objects to the planning grid and forces the route planner to avoid blocked cells.

## What Was Implemented

- `PanelCell` now stores `object_type`, `object_confidence`, and `risk_level`.
- `CleaningZoneMap.mark_object(...)` marks a cell as clear, caution, or blocked.
- `CleaningZoneMap.blocked_cells(clearance_cells=...)` inflates blocked cells for route clearance.
- `identify_objects_from_zone_map(...)` converts map state into object records.
- `apply_yolo_detections_to_zone_map(...)` can project detector boxes into the grid, but current YOLO weights remain diagnostic only.
- `plan_obstacle_aware_cleaning_route(...)` plans transit and clean actions using a grid route around obstacles.

## Demo Result

Command:

```bash
PYTHONPATH=src python3 scripts/demo_object_avoidance_route.py
```

Latest result:

- Identified objects: `14`
- Object summary:
  - `blind_or_shutter`: `5`
  - `protruding_balcony`: `9`
- Route steps: `37`
- Skipped targets: `0`
- Clearance violations: `0`

Outputs:

```text
outputs/object_avoidance_demo/zone_map.png
outputs/object_avoidance_demo/avoidance_route.png
outputs/object_avoidance_demo/identified_objects.json
outputs/object_avoidance_demo/route_plan.json
outputs/object_avoidance_demo/summary.json
```

## Meaning

This is now the trusted route-handling layer:

1. Perception identifies blocked/caution objects.
2. The map stores those objects with risk.
3. Blocked objects are inflated by configurable clearance.
4. The planner routes around inflated blocked regions.
5. Cleaning actions are emitted only at reachable cleanable cells.

YOLO is not trusted yet for object identification. It can feed this interface later after better training or a better dataset.

## Next Engineering Step

Connect the route steps to ROS/PX4:

- `transit` -> bounded facade-frame movement.
- `clean` -> hold position, confirm standoff, activate cleaning actuator.
- `caution` cells -> lower speed and increase standoff.
- skipped targets -> report to operator instead of forcing unsafe cleaning.
