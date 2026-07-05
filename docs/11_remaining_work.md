# Remaining Work

## Done

- Master prompt converted into project architecture and milestones.
- WSL/ROS/Gazebo compatibility stabilized without deleting old installs.
- ROS Humble + `ros_gz` bridge installed.
- Gazebo facade world validates.
- ROS package builds.
- Synthetic facade perception works.
- Cleaning-zone map now separates glass, concrete, frame, unknown, and obstacles.
- Path planner now cleans dirty glass only and skips non-cleanable areas.
- Object identification now records object type, confidence, and risk level.
- Obstacle-aware route planner now detours around blocked cells with configurable clearance.
- Object-avoidance demo verifies zero clearance violations.
- CMP Facade Database downloaded and indexed.
- CMP labels converted into UAV cleaning classes.
- CMP balcony/blind boxes converted into a YOLO obstacle dataset.
- YOLO11n smoke training completed and produced reusable detector weights.
- YOLO obstacle inference wrapper added.
- Safety layer and fault demo implemented.
- PPO training runs, but does not pass baseline gate yet.

## Left

- Train SegFormer on converted CMP cleaning masks. Started and smoke-verified.
- Redesign obstacle detection. YOLO balcony/blind training was attempted on GPU and failed its overfit diagnostic, so the next route should be segmentation/tiled detection after label QA.
- Add MiDaS depth estimation and LiDAR scale anchoring.
- Replace OpenCV heuristic with learned segmentation output.
- Add real building photo ingestion workflow.
- Improve PPO with CNN/map observation and curriculum learning.
- Connect object-aware route steps to ROS/PX4 waypoint or velocity commands.
- Connect planner outputs to PX4 offboard velocity commands.
- Add cleaning actuation model: wiper/water-jet trigger and reservoir depletion.
- Run Gazebo closed-loop demo: perception -> planner -> safety -> offboard control.
- Add final report/video/demo assets.

## Immediate Next Step

Run a larger SegFormer training job on all 606 CMP cleaning masks when GPU or long CPU time is available.

Current trained model:

- `models/segformer_cleaning`
- 120-sample staged CPU run
- 96 px images
- 1 epoch
- validation pixel accuracy: `0.439`

SegFormer now connects to `CleaningZoneMap` and emits a cleaning path.

Smoke verification completed:

- `models/segformer_cleaning_smoke`
- `outputs/segformer_smoke/predicted_cleaning_mask.png`
- `outputs/segformer_smoke/predicted_cleaning_overlay.png`

Added next bridge:

- `scripts/analyze_building_with_segformer.py` converts SegFormer predictions into `CleaningZoneMap` plus `cleaning_path.json`.
- `scripts/infer_yolo_obstacles.py` converts YOLO predictions into `detections.json` plus an obstacle overlay.

Latest learned-pipeline outputs:

- `outputs/segformer_building_analysis/segformer_overlay.png`
- `outputs/segformer_building_analysis/cleaning_zone_map.png`
- `outputs/segformer_building_analysis/cleaning_path.json`

Object avoidance outputs:

- `outputs/object_avoidance_demo/avoidance_route.png`
- `outputs/object_avoidance_demo/identified_objects.json`
- `outputs/object_avoidance_demo/route_plan.json`
- Latest demo: `14` identified objects, `37` route steps, `0` clearance violations.

YOLO obstacle pipeline status:

- Dataset: `data/processed/cmp_yolo_obstacles`
- Classes: `balcony`, `blind`
- Boxes: `1872` balcony, `4425` blind
- Split: `516` train images, `90` validation images
- Smoke model: `runs/detect/models/yolo_obstacles_smoke/weights/best.pt`
- Smoke metrics after one fractional CPU epoch: mAP is effectively zero, so the model is not production-ready yet.
- Full GPU model: `models/yolo_obstacles_full/weights/best.pt`
- Full GPU metrics: mAP50 `0.00285`, mAP50-95 `0.000607`.
- Overfit diagnostic: `models/yolo_obstacles_overfit32/weights/best.pt`
- Overfit diagnostic metrics: mAP50 `0.0574`, mAP50-95 `0.0188`.
- Verdict: current YOLO box setup is not reliable enough for planning.
