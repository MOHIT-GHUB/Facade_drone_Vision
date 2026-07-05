# Autonomous Facade-Cleaning UAV

Simulation-first project for an autonomous skyscraper facade-cleaning UAV. The goal is a closed-loop stack:

1. Perception fusion produces a cleaning-zone map.
2. RL coverage planning chooses velocity or waypoint actions.
3. PX4 offboard control tracks those actions.
4. Cleaning actuation runs under an independent safety layer.

This repository follows the master prompt in `docs/00_master_prompt_trace.md`.

## Current status

- Workspace was empty at project start except for `.git`.
- Codex could read the master prompt from `C:\Users\mohit\Downloads\facade_cleaning_uav_master_prompt.md`.
- `Ubuntu-22.04-LTS` is visible now. ROS Humble is installed, Gazebo Harmonic is installed, and the project should use the conservative Humble/Fortress bridge route documented in `docs/07_ros_gazebo_compatibility.md`.
- Windows Python is available, but NumPy/OpenCV/Gymnasium/Stable-Baselines3 are not installed in the current Windows environment.

## Repository map

- `docs/`: requirements, architecture, environment report, milestone log, and runbook.
- `src/facade_uav/`: Python core for map representation, safety, perception, RL, and control interfaces.
- `ros2_ws/src/facade_cleaning_uav/`: ROS 2 package scaffold for later Humble/Gazebo/PX4 integration.
- `simulation/gazebo/`: Gazebo world scaffold.
- `cad/solidworks/`: SolidWorks macro and shared payload parameters for the quadcopter cleaning payload.
- `scripts/`: environment checks and smoke tests.
- `requirements.txt`: Python dependencies for the OpenCV/RL workstreams.

## Quick verification

Run this now from PowerShell:

```powershell
python scripts\smoke_test_core.py
```

Expected result:

```text
core smoke test passed
```

Run the full WSL verification:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_all_verification.ps1
```

Run the SolidWorks/CAD dry-run:

```bash
PYTHONPATH=src python3 scripts/generate_solidworks_quadcopter.py --dry-run
```

This validates the water-jet/blower payload mass budget and writes:

- `outputs/cad/quadcopter_payload_spec.json`

Open the SolidWorks macro from:

- `cad/solidworks/facade_cleaning_quadcopter_generator.vba`

Run the interview simulation world:

```bash
gz sim -r simulation/gazebo/interview_facade_cleaning_world.sdf
```

Or through ROS 2:

```bash
ros2 launch facade_cleaning_uav interview_demo.launch.py
```

Analyze a facade/building image:

```bash
PYTHONPATH=src python3 scripts/analyze_building_image.py --input path/to/building.jpg --output-dir outputs/building_analysis_real
```

The analyzer marks cleanable glass separately from concrete/frame/unknown skip zones, then writes a cleaning path JSON for dirty glass only.

Run the object-identification and avoidance-route demo:

```bash
PYTHONPATH=src python3 scripts/demo_object_avoidance_route.py
```

Outputs:

- `outputs/object_avoidance_demo/identified_objects.json`
- `outputs/object_avoidance_demo/route_plan.json`
- `outputs/object_avoidance_demo/avoidance_route.png`

The route planner inflates blocked cells by a clearance radius, detours around them, and keeps caution objects identified for later speed/standoff handling.

Run the closed-loop mission demo:

```bash
PYTHONPATH=src python3 scripts/run_closed_loop_mission_demo.py
```

Outputs:

- `outputs/closed_loop_mission/closed_loop_zone_map.png`
- `outputs/closed_loop_mission/identified_objects.json`
- `outputs/closed_loop_mission/route_plan.json`
- `outputs/closed_loop_mission/nominal_execution.json`
- `outputs/closed_loop_mission/fault_execution.json`

This is the current v1 end-to-end proof: fused perception map -> object identification -> clearance-aware route -> safety shield -> offboard velocity command -> cleaning actuation log. The injected gust case must trigger the independent safety layer.

Download the selected facade segmentation dataset:

```bash
python3 scripts/download_cmp_facade.py
python3 scripts/prepare_cmp_facade_index.py
python3 scripts/convert_cmp_to_cleaning_masks.py
```

Smoke-train SegFormer cleaning segmentation:

```bash
PYTHONPATH=src CUDA_VISIBLE_DEVICES= python3 scripts/train_segformer_cleaning.py --limit 12 --epochs 1 --image-size 128 --batch-size 2 --output-dir models/segformer_cleaning_smoke
PYTHONPATH=src CUDA_VISIBLE_DEVICES= python3 scripts/infer_segformer_cleaning.py --model-dir models/segformer_cleaning_smoke --input data/processed/cmp_cleaning/images/cmp_b0001.jpg --output-dir outputs/segformer_smoke
```

Analyze a building image with a trained SegFormer cleaning model:

```bash
PYTHONPATH=src CUDA_VISIBLE_DEVICES= python3 scripts/analyze_building_with_segformer.py --model-dir models/segformer_cleaning --input path/to/building.jpg --output-dir outputs/segformer_building_analysis
```

CPU-friendly staged SegFormer training that has been verified:

```bash
OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONPATH=src CUDA_VISIBLE_DEVICES= python3 scripts/train_segformer_cleaning.py --limit 120 --epochs 1 --image-size 96 --batch-size 4 --output-dir models/segformer_cleaning
```

Prepare and smoke-train the YOLO11 obstacle detector:

```bash
python3 scripts/convert_cmp_to_yolo_obstacles.py
~/.local/bin/yolo train model=yolo11n.pt data=data/processed/cmp_yolo_obstacles/data.yaml epochs=1 imgsz=320 batch=4 device=cpu workers=0 fraction=0.2 project=models name=yolo_obstacles_smoke exist_ok=True plots=False
PYTHONPATH=src python3 scripts/infer_yolo_obstacles.py --model runs/detect/models/yolo_obstacles_smoke/weights/best.pt --input data/processed/cmp_yolo_obstacles/images/val/cmp_b0013.jpg --confidence 0.001 --image-size 320 --output-dir outputs/yolo_obstacles_script_smoke
```

The one-epoch CPU detector is only a wiring proof. Use longer GPU training before trusting obstacle boxes in flight planning.

YOLO GPU training has now also been tested. The full CMP balcony/blind detector and a 32-image overfit diagnostic both performed poorly, so the current YOLO obstacle model must not be used for safety decisions. See `docs/13_training_run_log.md`.

## Install Python dependencies later

When network access is available:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Milestone order

1. M0: requirements and baseline review.
2. M2: Gazebo facade world plus scripted wall following.
3. M3: OpenCV cleaning-zone map pipeline.
4. M4: PPO coverage planner that beats lawnmower baseline.
5. M5: closed-loop Python/ROS 2 pipeline with safety fault injection.

Current docs to show progress:

- `docs/06_project_worklog.md`
- `docs/08_status_report.md`
- `docs/12_progress_evaluation.md`
- `docs/14_object_avoidance_route_handling.md`
- `docs/16_closed_loop_mission_demo.md`
- `docs/17_solidworks_and_interview_demo_plan.md`
- `docs/18_iterative_critique_checklist.md`
- `docs/19_teaching_todos_and_checkpoints.md`
- `docs/20_senior_engineer_teaching_guide.md`

M1 SolidWorks automation now has a macro and dry-run mass budget. The final `.SLDPRT` still requires running the macro inside SolidWorks on Windows.
