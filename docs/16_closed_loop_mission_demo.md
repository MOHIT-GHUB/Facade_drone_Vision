# Closed-Loop Mission Demo

Generated on 2026-07-05 IST.

## Purpose

This demo closes the v1 software loop without pretending that the unpassed
research gates are solved. It proves that the trusted stack can pass data
through these layers:

```text
fused perception map -> object identification -> obstacle-aware route ->
independent safety layer -> offboard velocity command -> cleaning actuation log
```

## Why This Was Added

The master prompt asks for more than separate perception, planner, RL, and ROS
pieces. The project needed one auditable mission run where the planner output is
actually consumed by safety/control/actuation logic and where a fault can stop
the mission independently of the planner.

## Command

```bash
PYTHONPATH=src python3 scripts/run_closed_loop_mission_demo.py
```

The full verification wrapper also runs this command:

```bash
bash scripts/run_all_verification.sh
```

## What It Does

1. Builds a simulated fused perception grid with glass, blocked protrusions,
   caution objects, and dirty cleaning targets.
2. Identifies facade objects with object type, risk level, confidence, and grid
   cells.
3. Plans a route with one-cell inflated obstacle clearance.
4. Skips cleaning targets that fall inside the inflated obstacle zone.
5. Converts route steps into clamped velocity commands.
6. Runs each command through the independent safety layer.
7. Logs water-jet actuation only for allowed clean steps.
8. Re-runs the mission with an injected gust to verify the wind-abort path.

## Latest Result

Output folder:

```text
outputs/closed_loop_mission/
```

Latest summary:

- Identified objects: `14`
- Route steps requested: `20`
- Clearance violations: `0`
- Safe cleaning events: `2`
- Nominal safety overrides: `0`
- Fault-run safety overrides: `1`
- Fault injected: wind gust above abort threshold

Important artifacts:

```text
outputs/closed_loop_mission/closed_loop_zone_map.png
outputs/closed_loop_mission/identified_objects.json
outputs/closed_loop_mission/route_plan.json
outputs/closed_loop_mission/nominal_execution.json
outputs/closed_loop_mission/fault_execution.json
outputs/closed_loop_mission/summary.json
```

## Interpretation

This is the current v1 integration proof. It is conservative: if a dirty glass
target is too close to a blocked object after clearance inflation, it is skipped
instead of cleaned. That behavior is intentional because route safety must be
independent of learned perception or RL optimism.

## What This Does Not Claim

- It is not a real hardware flight.
- It is not a PX4 SITL flight with physical dynamics.
- It does not claim the current YOLO obstacle detector is reliable.
- It does not claim PPO has beaten the deterministic baseline yet.

## Next Upgrade

The next engineering step is to replace the synthetic fused grid in this demo
with the real image analyzer output and then publish the same route/command log
from ROS 2 nodes during Gazebo/PX4 SITL.
