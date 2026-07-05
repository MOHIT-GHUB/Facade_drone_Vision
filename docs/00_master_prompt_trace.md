# Master Prompt Trace

Source file:

`C:\Users\mohit\Downloads\facade_cleaning_uav_master_prompt.md`

Read by Codex on 2026-07-05 IST.

## Non-negotiable project intent

Build a simulation-first autonomous facade-cleaning UAV project that feels stronger than a generic "drone plus YOLO plus RL" demo. The final system should close the loop:

```text
camera/thermal/lidar -> perception fusion -> RL planner -> PX4/offboard control -> cleaning actuation -> feedback
```

## Scope for v1

In scope:

- Mock skyscraper facade environment.
- Cleaning-zone map from visual/thermal/depth signals.
- PPO-style coverage planner with reservoir-aware reward shaping.
- Independent safety layer for geofence, standoff, wind, battery, and reservoir constraints.
- ROS 2/Gazebo/PX4 integration scaffold.
- Documentation that explains assumptions, alternatives, and why each choice was made.

Out of scope for v1:

- Real urban deployment.
- Multi-UAV swarms.
- BVLOS certification.
- Real hardware flight on an actual building.

## Novelty chosen for v1

Primary novelty: reservoir-aware replanning.

Why this is defensible:

- Facade cleaning has a payload whose mass changes through the mission.
- The changing reservoir affects both coverage decisions and flight dynamics.
- Most simple coverage-planning projects ignore this coupling.

Secondary novelty kept available:

- Thermal anomaly channel for cleaning plus facade-health monitoring.
- Wind curriculum and domain randomization for urban facade robustness.

## Implementation choices

- Use OpenCV first for a deterministic cleaning-zone map baseline.
- Add YOLOv11, SegFormer, and MiDaS as optional high-performance model backends after the pipeline is testable.
- Keep the core safety layer independent from RL.
- Use PPO for the learning agent because it is stable enough for continuous actions while remaining practical to iterate.
- Keep a lawnmower baseline for honest comparison.

## Evidence trail

Every milestone should update:

- `docs/04_milestone_log.md`
- `docs/05_runbook.md`
- Any relevant config under `ros2_ws/src/facade_cleaning_uav/config/`
