# Project Worklog

## 2026-07-05 - Project start

What was done:

- Read the master prompt.
- Confirmed the repo was essentially empty.
- Checked the visible environment from Codex.
- Found Python 3.13.13 available.
- Found WSL/Ubuntu not visible to this sandbox.
- Found NumPy, OpenCV, Gymnasium, Stable-Baselines3 not installed.
- Created the initial project scaffold.
- Added dependency-free core smoke test.

Design decisions:

- Start with a deterministic OpenCV baseline before adding heavy YOLO/SegFormer/MiDaS inference.
- Keep a pure-Python coverage environment so reward design can be tested even before Gymnasium is installed.
- Keep the safety layer independent from learned policy output.
- Choose reservoir-aware replanning as the v1 novelty.

Next work:

- Install dependencies.
- Run Gymnasium/PPO trainer.
- Add facade screenshots or simulated frames for OpenCV perception.
- Build ROS 2 messages and real node wiring once Ubuntu/ROS is visible.

## 2026-07-05 - WSL/ROS/Gazebo compatibility pass

What was found:

- `Ubuntu-22.04-LTS` is accessible.
- ROS Humble is installed at `/opt/ros/humble`.
- `ros2` works after sourcing `/opt/ros/humble/setup.bash`.
- Gazebo Harmonic is installed through `gz-harmonic`; `gz sim` reports `8.9.0`.
- `colcon` is not installed.
- `ros-humble-ros-gz` is not installed.
- Sudo requires the user's WSL password, so installation must be run manually inside Ubuntu.

Decision:

- Do not delete old WSL distros or Gazebo Harmonic yet.
- Use the conservative Humble/Fortress bridge path for the project.
- Install `ros-humble-ros-gz` and `python3-colcon-common-extensions` only after reviewing the dry-run shown by `scripts/install_humble_fortress_prereqs.sh`.

Evidence:

- `scripts/wsl_ros_gazebo_audit.sh`
- `scripts/source_humble_fortress_env.sh`
- `scripts/install_humble_fortress_prereqs.sh`
- `docs/07_ros_gazebo_compatibility.md`

## 2026-07-05 - Full verification pass

What was installed:

- `ros-humble-ros-gz` via WSL root.
- Ignition/Fortress Gazebo 6 bridge libraries.
- `python3.10-venv`.
- User-level Python packages for perception/RL: OpenCV headless, Gymnasium, Stable-Baselines3, Torch, Matplotlib, Pillow.
- User-level `colcon-common-extensions`.

What was implemented:

- Synthetic facade generator.
- OpenCV cleaning-zone demo.
- Safety fault injection demo.
- PPO trainer and evaluation script.
- Greedy nearest-dirty fallback planner.
- ROS status publisher nodes.
- ROS Gazebo simulation launch scaffold.
- Full verification script.

Verification:

- `bash scripts/run_all_verification.sh` completed successfully.
- ROS package `facade_cleaning_uav` builds with colcon.
- SDF worlds validate.
- Safety layer triggers for standoff, wind, reservoir, battery, and LiDAR faults.

Important finding:

- PPO training runs, but the trained smoke policy does not beat baseline yet.
- Current trusted planner for a demo is greedy nearest-dirty fallback, not PPO.

## 2026-07-05 - Learned facade perception expansion

What was implemented:

- CMP Facade Database was downloaded, indexed, and converted into UAV cleaning masks.
- SegFormer cleaning segmentation was smoke-trained and connected to `CleaningZoneMap`.
- A staged CPU SegFormer model was trained on 120 samples at 96 px for 1 epoch.
- CMP balcony/blind XML boxes were converted into a YOLO obstacle dataset.
- Ultralytics was installed in WSL.
- YOLO11n obstacle detector smoke training completed on a 20% training fraction for 1 CPU epoch.
- A reusable YOLO obstacle inference wrapper now writes `detections.json` and `obstacle_overlay.png`.

Verification:

- `powershell -ExecutionPolicy Bypass -File scripts\run_all_verification.ps1` completed successfully.
- YOLO dataset conversion produced `516` train images and `90` validation images.
- YOLO obstacle labels contain `1872` balcony boxes and `4425` blind boxes.
- YOLO inference script verified on `cmp_b0013.jpg`.

Important finding:

- The YOLO smoke model is a pipeline proof only. One fractional CPU epoch produced effectively zero useful mAP, so real obstacle detection still needs longer GPU training and more obstacle classes.

## 2026-07-05 - Closed-loop route, safety, and actuation pass

Why this was needed:

- The master prompt requires an end-to-end loop, not only separate perception,
  planning, and safety modules.
- The previous object-avoidance route allowed cleaning targets inside inflated
  obstacle clearance. That was useful for diagnostics, but too permissive for a
  serious safety story.

What was implemented:

- `find_grid_route(...)` now treats inflated obstacle clearance as hard blocked
  for the goal by default.
- `plan_obstacle_aware_cleaning_route(...)` now skips dirty targets that are
  unreachable under the requested clearance.
- `validate_route_clearance(...)` checks every emitted route step.
- `facade_uav.integration.closed_loop` converts route steps into clamped
  velocity commands, safety decisions, and water-jet actuation events.
- `scripts/run_closed_loop_mission_demo.py` produces nominal and fault mission
  logs.
- Full verification now includes object avoidance and closed-loop mission checks.

Latest result:

- Object avoidance: `14` identified objects, `20` route steps, `0` clearance
  violations.
- Closed-loop nominal run: `20` events, `2` safe cleaning events, `0` safety
  overrides.
- Closed-loop fault run: injected gust caused `1` safety override.

Evidence:

- `docs/16_closed_loop_mission_demo.md`
- `outputs/closed_loop_mission/summary.json`
- `outputs/closed_loop_mission/nominal_execution.json`
- `outputs/closed_loop_mission/fault_execution.json`
