# Milestone Log

Updated on 2026-07-05 IST.

## M0 - Requirements and baseline review

Status: passed for v1 documentation and scaffold gate.

Completed:

- Master prompt read and traced.
- Scope extracted.
- v1 novelty selected: reservoir-aware replanning.
- Initial metrics selected.
- Environment checked from Codex sandbox and WSL.
- ROS/Gazebo compatibility plan created.
- Full verification wrapper now checks core logic, perception, object
  avoidance, closed-loop mission execution, safety faults, RL evaluation, SDF
  validation, and ROS build.

Evidence:

- `docs/00_master_prompt_trace.md`
- `docs/01_requirements.md`
- `docs/02_architecture.md`
- `docs/03_environment_report.md`
- `docs/07_ros_gazebo_compatibility.md`
- `scripts/run_all_verification.sh`

## M1 - Mechanical/SolidWorks automation

Status: planned, blocked by local SolidWorks availability.

Notes:

- Needs SolidWorks on Windows.
- Recommended route is Python plus `pywin32` COM once mass/CG model is final.
- v1 software is structured so reservoir mass depletion is already represented
  in planning and actuation logs before CAD automation is added.

## M2 - Simulation

Status: scaffolded and validation-passed.

Completed:

- Gazebo facade SDF validates.
- ROS 2 package builds under Humble.
- Conservative Humble/Fortress compatibility route is documented.

Next:

- Connect closed-loop route command logs to PX4 SITL offboard commands.
- Test scripted wall following with the facade world open in Gazebo.

## M3 - Perception

Status: usable deterministic baseline; learned backends wired but not final.

Completed:

- Synthetic facade OpenCV cleaning-zone demo runs.
- Building-image analysis separates glass to clean from concrete/frame/unknown
  areas to skip.
- Object identification records type, confidence, risk level, and cells.
- SegFormer bridge is wired and smoke-trained.
- YOLO obstacle detector training pipeline is wired, but current weights are not
  reliable enough for planning.

## M4 - RL

Status: scaffolded; PPO gate not passed.

Completed:

- Gymnasium and Stable-Baselines3 PPO training run.
- PPO smoke model can be evaluated.
- Lawnmower and greedy nearest-dirty baselines are available for honest
  comparison.

Finding:

- PPO currently does not beat the deterministic baseline on held-out evaluation.
- Greedy nearest-dirty is the trusted v1 planner until PPO improves.

Next:

- Add richer map observation or CNN policy.
- Add curriculum training.
- Save best PPO model via evaluation callback.
- Evaluate across multiple held-out seeds.

## M5 - Integration and safety

Status: v1 Python closed-loop passed; ROS/Gazebo closed-loop remains next.

Completed:

- Safety layer handles standoff, geofence, wind, battery, reservoir, and LiDAR
  validity.
- Object-aware route planner detours around inflated blocked cells.
- Unsafe dirty targets inside obstacle clearance are skipped.
- Closed-loop mission demo converts route steps to safety-gated velocity
  commands and actuation logs.
- Injected gust fault triggers an independent safety override.

Evidence:

- `scripts/run_closed_loop_mission_demo.py`
- `outputs/closed_loop_mission/summary.json`
- `docs/16_closed_loop_mission_demo.md`

Next:

- Turn the Python closed-loop demo into ROS 2 node-to-node execution.
- Connect planner outputs to PX4 offboard velocity or waypoint commands.
