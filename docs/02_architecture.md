# System Architecture

## Data flow

```text
RGB camera
thermal camera
lidar or laser range
        |
        v
perception fusion
        |
        v
cleaning-zone map
        |
        v
RL coverage planner
        |
        v
safety layer
        |
        v
PX4 offboard command
        |
        v
cleaning actuation
```

## Core interfaces

### Cleaning-zone map

Each panel cell stores:

- dirty confidence
- obstacle flag
- object type and confidence
- risk level: clear, caution, or blocked
- depth or standoff estimate
- thermal anomaly flag
- cleaned flag

### Object identification and route handling

Object identification feeds the same cleaning-zone map used by the planner.
This matters because perception is only useful if the route changes.

Current object sources:

- OpenCV/SegFormer grid state: frame, obstacle, thermal anomaly, unknown skip.
- YOLO detections can be projected into grid cells, but current YOLO weights are diagnostic only.
- Manual or simulation objects can be marked directly on the map for tests.

Risk handling:

- `blocked`: no transit through the cell.
- `caution`: route may pass, but later control should slow down or increase standoff.
- `clear`: normal route.

The object-aware route planner inflates blocked cells by a configurable grid-cell clearance radius and finds a detour route before emitting cleaning actions.

### RL observation

- Cleaning-zone map summary.
- UAV pose.
- Current standoff.
- Remaining reservoir.
- Battery percentage.
- Wind estimate.

### RL action

For v1:

- continuous facade-frame velocity command: `vx`, `vz`, `standoff_rate`

For ROS 2/PX4 integration:

- convert action to a bounded offboard velocity or waypoint command.

### Safety layer

The safety layer sees proposed commands and mission state. It can:

- pass command unchanged
- clamp command
- hold position
- return to base
- abort mission

The RL policy is never the only thing preventing a collision.

Object-aware route planning happens before the safety shield. The planner avoids known blocked cells; the safety layer remains the independent final guard for standoff, wind, geofence, battery, reservoir, and LiDAR faults.

## Why this architecture

Perception has to produce a map before coverage can be planned. The planner has to produce motion intent before PX4 can control the aircraft. The safety layer belongs between the planner and controller because it must remain independent from learned behavior.
