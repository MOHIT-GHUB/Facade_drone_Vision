# SolidWorks And Interview Demo Plan

Generated on 2026-07-06 IST.

## Purpose

This document explains the new interview-facing mechanical and simulation demo
assets:

```text
SolidWorks macro + mass budget -> Gazebo interview world -> ROS demo launch ->
closed-loop cleaning proof
```

## SolidWorks Quadcopter Generator

Main macro:

```text
cad/solidworks/facade_cleaning_quadcopter_generator.vba
```

Shared parameters:

```text
cad/solidworks/quadcopter_payload_parameters.json
```

Dry-run validation:

```bash
PYTHONPATH=src python3 scripts/generate_solidworks_quadcopter.py --dry-run
```

Latest dry-run result:

- Wet mass: `4.202 kg`
- Reservoir: `1.2 L`
- Max thrust: `72.0 N`
- Thrust-to-weight: `1.747`
- CG Y offset: `0.001 m`
- CG status: within limit

The first check rejected the weaker motor assumption because thrust-to-weight was
only `1.116`. The motor thrust assumption was raised to a heavier-lift class,
which is the correct engineering refinement before showing the payload as
credible.

## What The Macro Generates

- X-frame quadcopter body.
- Four motor pods and propeller discs.
- CG-centered water reservoir.
- High-pressure pump module.
- Front water-jet spray bar.
- Left and right blower ducts.
- RGB/thermal/LiDAR gimbal pod.
- Quick-connect water hose dock.
- Landing skids.
- SolidWorks custom properties linking the part to this project.

## Interview Gazebo World

Standalone world:

```bash
gz sim -r simulation/gazebo/interview_facade_cleaning_world.sdf
```

ROS launch:

```bash
source /opt/ros/humble/setup.bash
cd /mnt/c/Users/mohit/OneDrive/Documents/Facade_drone_Vision/ros2_ws
source install/setup.bash
ros2 launch facade_cleaning_uav interview_demo.launch.py
```

The world contains:

- Start pad.
- Water refill station and quick-connect hose.
- Payload-equipped facade-cleaning UAV visual model.
- Washable glass facade.
- Dirty target patches.
- Concrete skip panels.
- AC-unit and ledge obstacles.
- Route markers for start, refill, scan, and clean points.

## Generated Interview Storyboard

```bash
python3 scripts/create_interview_demo_storyboard.py
```

Outputs:

```text
outputs/interview_demo/interview_demo_storyboard.md
outputs/interview_demo/interview_demo_storyboard.json
```

Use the storyboard to narrate the demo:

1. UAV starts on pad and verifies water connection.
2. UAV takes off and scans the facade.
3. Perception separates dirty glass from concrete, frames, and obstacles.
4. Planner creates a safe route with obstacle clearance.
5. Water jet and blower clean only approved targets.
6. Injected gust triggers independent safety override.

## Verification

The full project check now validates:

- SolidWorks CAD dry-run mass budget.
- Required CAD payload feature names.
- Standalone and ROS copies of the interview SDF world.
- Gazebo SDF parser validity.
- ROS package build with the interview launch file installed.
- Storyboard generation.

Command:

```bash
bash scripts/run_all_verification.sh
```

## Honest Limits

- The SolidWorks macro is ready, but the final `.SLDPRT` requires running it in
  SolidWorks on Windows.
- The interview world is visual and validation-ready; PX4 dynamic flight inside
  Gazebo remains the next integration gate.
- PPO is not claimed as final because it still does not beat the deterministic
  baseline.
- YOLO obstacle detection remains diagnostic only because its mAP and overfit
  checks failed.

