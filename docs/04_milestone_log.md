# Milestone Log

## M0 - Requirements and baseline review

Status: in progress.

Completed:

- Master prompt read.
- Scope extracted.
- v1 novelty selected: reservoir-aware replanning.
- Initial metrics selected.
- Environment checked from Codex sandbox.
- WSL `Ubuntu-22.04-LTS` checked after user confirmed installed distros.
- ROS/Gazebo compatibility plan created.

Evidence:

- `docs/00_master_prompt_trace.md`
- `docs/01_requirements.md`
- `docs/02_architecture.md`
- `docs/03_environment_report.md`
- `docs/07_ros_gazebo_compatibility.md`

Next:

- Run core smoke test.
- Install Python dependencies.
- Build deterministic OpenCV cleaning-zone map demo.
- Manually install `ros-humble-ros-gz` and `python3-colcon-common-extensions` inside WSL.

## M1 - Mechanical/SolidWorks automation

Status: planned.

Notes:

- Needs SolidWorks on Windows.
- Recommended route is Python plus `pywin32` COM once mass/CG model is final.
- v1 code should produce mass budget data even before CAD automation.

## M2 - Simulation

Status: scaffolded.

Next:

- Run `bash scripts/install_humble_fortress_prereqs.sh` inside `Ubuntu-22.04-LTS`.
- Load `simulation/gazebo/facade_world.sdf` in Gazebo.
- Add PX4 model bridge.
- Test scripted wall following.

## M3 - Perception

Status: scaffolded.

Next:

- Install OpenCV.
- Run facade image/video through `facade_uav.perception.opencv_cleaning_zone`.
- Measure FPS.

## M4 - RL

Status: scaffolded; PPO gate not passed.

Completed:

- Install Gymnasium and Stable-Baselines3.
- Train PPO smoke policy.
- Compare against lawnmower and greedy nearest-dirty baseline.

Finding:

- PPO currently does not beat baseline on held-out seed 11.
- Greedy nearest-dirty beats lawnmower on reward while matching coverage.

Next:

- Add richer map observation or CNN policy.
- Add curriculum training.
- Save best PPO model via evaluation callback.

## M5 - Integration and safety

Status: scaffolded.

Next:

- Turn Python modules into ROS 2 nodes.
- Inject wind and LiDAR faults.
- Confirm safety layer overrides unsafe commands.
