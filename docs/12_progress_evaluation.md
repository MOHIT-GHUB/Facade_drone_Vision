# Progress Evaluation

Generated on 2026-07-05.

## Visual Board

Main board:

```text
outputs/progress_evaluation/progress_board.png
```

This board compares:

- Synthetic facade input.
- OpenCV clean/skip zone map.
- CMP facade dataset labels.
- SegFormer learned overlay.
- SegFormer-to-grid cleaning zone map.
- YOLO obstacle smoke overlay.

## Current Verdict

The project foundation is working. The reliable demo path today is:

1. Synthetic or input facade image.
2. Cleaning-zone map generation.
3. Object identification into clear/caution/blocked cells.
4. Obstacle-aware route planning with clearance detours.
5. Closed-loop safety-gated command generation and cleaning actuation logs.
6. Safety override checks.
7. SolidWorks payload macro and mass-budget dry-run.
8. Interview Gazebo world and ROS launch validation.

The learned perception stack is partially working:

- SegFormer is connected to the planner and produces a cleaning-zone map.
- YOLO obstacle detection pipeline trains and runs, but the current smoke model is not accurate.

## Layer Evaluation

### OpenCV Cleaning-Zone Baseline

Status: usable baseline.

Latest metrics:

- Cleanable glass cells: `61`
- Concrete skip cells: `9`
- Frame/obstacle skip cells: `26`
- Dirty cleaning waypoints: `58`

This layer looks coherent on the synthetic facade and is currently the safest perception demo.

### SegFormer Cleaning Segmentation

Status: wired and demonstrable, but undertrained.

Latest staged model:

- Training subset: `120` CMP samples
- Image size: `96 px`
- Epochs: `1`
- Validation pixel accuracy: `0.439`

Latest sample path:

- Cleanable glass cells: `17`
- Cleaning waypoints: `17`

This is a real learned segmentation bridge, but it needs longer GPU training before it should replace the OpenCV baseline.

### YOLO Obstacle Detector

Status: pipeline proof only.

Dataset conversion is good:

- Train images: `516`
- Validation images: `90`
- Balcony boxes: `1872`
- Blind boxes: `4425`

Smoke model status:

- Model: YOLO11n
- Training: 1 CPU epoch on 20% fraction
- Normal confidence `0.25`: `0` detections
- Very low confidence `0.001`: `298` detections on one sample, all extremely weak
- Confidence range: about `0.0015` to `0.0064`

The weird dense output layer is therefore not correct perception. It happened because the threshold was lowered too far to verify that inference and rendering were wired. For real use, this model needs full training.

### Planner And RL

Status: deterministic planner works; object-aware route handling works; PPO does not pass the gate yet.

Latest evaluation:

- Lawnmower: coverage `0.989`, reward `720.6`
- Greedy nearest-dirty: coverage `0.989`, reward `802.1`
- PPO smoke policy: coverage `0.057`, reward `-370.7`

Use greedy nearest-dirty for the demo. PPO remains research work.

## What To Judge Visually

Use these files:

- `outputs/progress_evaluation/progress_board.png`
- `outputs/building_analysis/cleaning_zone_map.png`
- `outputs/object_avoidance_demo/avoidance_route.png`
- `outputs/object_avoidance_demo/identified_objects.json`
- `outputs/object_avoidance_demo/route_plan.json`
- `outputs/segformer_building_analysis/segformer_overlay.png`
- `outputs/segformer_building_analysis/cleaning_zone_map.png`
- `outputs/yolo_obstacles_threshold_025/obstacle_overlay.png`
- `outputs/yolo_obstacles_script_smoke/obstacle_overlay.png`

## Next Correct Step

The first proper YOLO GPU training and a 32-image overfit diagnostic were completed.

Result:

- Full YOLO11n GPU run: mAP50 `0.00285`.
- 32-image overfit run: mAP50 `0.0574`.
- Normal confidence inference still produces no reliable boxes.

Do not continue blind YOLO training on the same labels. The next correct move is to shift obstacle handling toward segmentation masks, higher-resolution/tiled experiments only after label QA, and fusion with the existing clean-skip grid.

Updated visual board:

```text
outputs/progress_evaluation/yolo_training_evaluation_board.png
```

Object-avoidance demo result:

- Identified objects: `14`
- Object types: `blind_or_shutter`, `protruding_balcony`
- Route steps after conservative clearance skipping: `20`
- Clearance violations: `0`

The object-aware route planner is now the trusted route-handling layer. YOLO remains diagnostic until a better obstacle perception model is trained.

### Closed-Loop Mission Demo

Status: v1 integration proof passed.

Latest result:

- Pipeline: perception map -> object identification -> route -> safety -> offboard velocity command -> cleaning actuation log.
- Nominal events: `20`
- Safe cleaning events: `2`
- Nominal safety overrides: `0`
- Fault-run safety overrides: `1`
- Clearance violations: `0`

Use these files:

- `outputs/closed_loop_mission/closed_loop_zone_map.png`
- `outputs/closed_loop_mission/summary.json`
- `outputs/closed_loop_mission/nominal_execution.json`
- `outputs/closed_loop_mission/fault_execution.json`

This is the strongest current proof that the project is no longer only separate
modules. The remaining integration jump is to drive PX4 SITL with the same
commands inside Gazebo.

### SolidWorks And Interview World

Status: interview-demo assets added and validation-passed.

Latest mechanical check:

- Wet mass: `4.202 kg`
- Reservoir: `1.2 L`
- Thrust-to-weight: `1.747`
- CG Y offset: `0.001 m`
- Status: pass

Use these files:

- `cad/solidworks/facade_cleaning_quadcopter_generator.vba`
- `outputs/cad/quadcopter_payload_spec.json`
- `simulation/gazebo/interview_facade_cleaning_world.sdf`
- `outputs/interview_demo/interview_demo_storyboard.md`

The important critique note: the first motor assumption failed the lift-margin
check. The current configuration only passed after increasing the motor thrust
assumption to a heavier-lift class.
