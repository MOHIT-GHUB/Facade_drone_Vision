# Real Facade Pipeline: What Comes Next

## What the current synthetic facade is

The synthetic facade is a generated test image. It is not the final product.

It exists so the pipeline can be tested without needing a real building dataset every time:

1. Generate facade-like image.
2. Detect surface classes.
3. Build cleaning-zone map.
4. Skip concrete/frame/unknown areas.
5. Plan path only over dirty cleanable glass.

## What a cleaning-zone map means

The cleaning-zone map is the decision layer between perception and planning.

Each grid cell stores:

- `surface_type`: `glass`, `concrete`, `frame`, or `unknown`
- `dirty_confidence`
- `obstacle`
- `depth_m`
- `thermal_anomaly`
- `cleaned`

Planner rule for v1:

```text
clean only dirty glass
skip concrete
skip frames
skip unknown surfaces
skip obstacles
```

## Current verified result

On the synthetic facade demo:

- Cleanable glass cells: `61`
- Concrete skip cells: `9`
- Frame/obstacle skip cells: `26`
- Cleaning waypoints generated: `58`

Outputs:

- `outputs/perception_demo/synthetic_facade.png`
- `outputs/perception_demo/cleaning_zone_map.png`
- `outputs/building_analysis/cleaning_path.json`

## How to analyze a real building image

Use:

```bash
cd /mnt/c/Users/mohit/OneDrive/Documents/Facade_drone_Vision
PYTHONPATH=src python3 scripts/analyze_building_image.py --input /path/to/building.jpg --output-dir outputs/building_analysis_real
```

This will produce:

- `cleaning_zone_map.png`
- `cleaning_path.json`
- `summary.json`

## Next engineering upgrade

The current semantic classifier is OpenCV heuristic-based. It is good for proving the interface, not enough for final accuracy.

Next model path:

1. Collect or create facade images with labels:
   - glass
   - concrete
   - metal frame
   - obstacle
   - dirty patch
   - clean glass
2. Use SegFormer for pixel-level facade material segmentation.
3. Use YOLOv11 for objects/obstacles such as AC units, ledges, ropes, protrusions.
4. Use MiDaS plus LiDAR scale anchoring for standoff/depth.
5. Fuse those into the same `CleaningZoneMap`.
6. Feed only cleanable dirty glass cells to the planner.

## Why this order matters

Planning before semantic filtering is dangerous. A planner that does not know the difference between glass and concrete will waste time, damage surfaces, or choose impossible cleaning paths.

So the correct order is:

```text
image -> semantic surface map -> cleaning-zone map -> skip mask -> path planning -> safety layer -> PX4/Gazebo
```
