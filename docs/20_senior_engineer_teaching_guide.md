# Senior Engineer Teaching Guide

Generated on 2026-07-06 IST.

This guide follows the teaching master prompt: never start from code, never skip
why, and always connect implementation to engineering reasoning.

You should not read this passively. At every `Mentor question`, stop and answer
before reading the next paragraph.

## Stage 0 - The Problem

### Real-world problem

Tall glass buildings get dirty, stained, and thermally stressed. Manual facade
cleaning is slow, risky, expensive, and weather-dependent. Workers are exposed
to height hazards, ropes, wind gusts, falling-object risk, and repetitive manual
work.

Mentor question: if you were responsible for a 40-floor glass building, what
would worry you more: cleaning quality, human safety, cost, or downtime?

The engineering problem is not "make a drone fly." The problem is:

```text
Safely identify what parts of a vertical facade should be cleaned, move near
the wall without collision, activate cleaning only where appropriate, and stop
when conditions become unsafe.
```

### Who needs it

- Building maintenance companies.
- High-rise facility managers.
- Robotics companies building facade inspection/cleaning products.
- Researchers studying close-proximity flight, perception, and coverage.

### Existing solutions

| Existing solution | Strength | Weakness |
|---|---|---|
| Rope-access workers | Flexible and proven | Human risk, slow, expensive |
| Gondola platforms | Stable, large water supply | Setup time, building-specific hardware |
| Ground pressure washers | Simple | Limited height |
| Basic drone spraying | Fast demonstration | Often unsafe, no real clean/skip reasoning |

### Why build this project

This project is a simulation-first proof that combines:

- Perception: identify glass, dirt, obstacles, and skip zones.
- Planning: choose a safe coverage path.
- Safety: independently reject unsafe commands.
- Mechanical payload: water jet, blower, reservoir, pump, sensors.
- Simulation: show the story in Gazebo/ROS.
- Documentation: make the trade-offs defensible in an interview.

Rebuild challenge: explain the project in one sentence without saying "AI",
"YOLO", "RL", or "OpenCV".

## Stage 1 - Requirement Engineering

### Functional requirements

| Requirement | Why it exists | Evidence |
|---|---|---|
| Build a cleaning-zone map | Planner needs structured state, not raw pixels | `src/facade_uav/cleaning_zone_map.py` |
| Separate cleanable glass from skip zones | Cleaning concrete/frames wastes water and can cause damage | `scripts/analyze_building_image.py` |
| Identify objects and risk | AC units, ledges, blinds, and openings affect route safety | `src/facade_uav/perception/object_identification.py` |
| Plan obstacle-aware route | Drone must not fly through inflated obstacle clearance | `src/facade_uav/planning/coverage_path.py` |
| Gate every command through safety | Learned or heuristic planner must not be the only safety layer | `src/facade_uav/safety_layer.py` |
| Log actuation and resource use | Reservoir and battery affect mission feasibility | `src/facade_uav/integration/closed_loop.py` |
| Provide CAD and simulation proof | Interviewers need visible system evidence | `cad/solidworks/`, `simulation/gazebo/` |

### Non-functional requirements

| Category | Requirement | Reason |
|---|---|---|
| Safety | Independent safety layer | Planner bugs should not cause collision |
| Testability | Pure Python core | Core logic can be tested without ROS/Gazebo |
| Explainability | Docs and logs | Interview defense and future maintenance |
| Reproducibility | Verification scripts | Avoid "it worked once" demos |
| Modularity | Separate perception/planning/safety/control | Each part can be replaced |
| Honesty | PPO/YOLO gates documented | Avoid fake claims |

### Success metrics

- Core smoke test passes.
- Closed-loop mission has zero clearance violations.
- Fault run triggers safety override.
- Gazebo SDF files validate.
- ROS package builds.
- CAD dry-run passes thrust-to-weight and CG checks.
- PPO is evaluated honestly against baselines.

### Failure conditions

- Cleaning route enters inflated obstacle clearance.
- Safety layer allows bad standoff, high wind, low battery, low reservoir, or invalid LiDAR.
- CAD mass budget has poor thrust-to-weight or CG offset.
- A trained detector is claimed as reliable without validation.
- ROS/Gazebo compatibility breaks the build.

Rebuild challenge: write five functional and five non-functional requirements
from memory.

## Stage 2 - Solution Ideation

### Option A: beginner monolith

One script reads an image, guesses dirt, prints waypoints, and claims a drone
can clean them.

Why it seems reasonable: it is fast.

Why it fails: no safety, no modularity, no simulation trace, no replaceable
perception backend, no interview defense.

### Option B: pure ROS/Gazebo first

Start with PX4 SITL, ROS topics, Gazebo models, and only later add perception.

Why it seems reasonable: it looks like robotics.

Why it fails early: integration complexity hides basic logic bugs. You can spend
days fighting environment issues before proving the cleaning logic.

### Option C: modular simulation-first stack

Build pure Python modules for map, planning, safety, and actuation logs. Then
bridge them into ROS/Gazebo.

Why it was chosen: each layer can be tested independently before integration.

Trade-off: the early demo is not yet true dynamic flight. It is honest and
testable, but PX4 closed-loop motion remains a later gate.

Decision:

```text
Pure Python core first -> ROS/Gazebo scaffold second -> CAD/interview world
third -> PX4 dynamic integration next.
```

Rebuild challenge: argue for Option C against a teammate who wants to start with
PX4 immediately.

## Stage 3 - System Design

### Architecture

```text
RGB/thermal/LiDAR or synthetic image
        |
        v
Perception and object identification
        |
        v
CleaningZoneMap
        |
        v
Obstacle-aware planner + RL research path
        |
        v
Safety layer
        |
        v
Offboard command shaping
        |
        v
Cleaning actuation log
        |
        v
Verification artifacts and ROS/Gazebo demo
```

### Why modules are separate

| Module | Responsibility | Why separate |
|---|---|---|
| `cleaning_zone_map` | State model | Every planner/perception backend can share it |
| `perception` | Build map from images or detections | Can replace OpenCV with SegFormer later |
| `planning` | Decide route | Can compare greedy, BFS, PPO |
| `safety_layer` | Reject unsafe commands | Must be independent of planner |
| `integration` | Execute route into command/actuation log | Proves loop closure |
| `mechanical` | Mass and payload assumptions | CAD and simulation need shared facts |
| `ros2_ws` | ROS launch/nodes | Robotics integration boundary |
| `simulation` | Gazebo world | Visual and physics environment |

### Coupling and cohesion

Good cohesion: `SafetyLayer.evaluate` only answers "is this command safe?"

Acceptable coupling: `execute_closed_loop_route` depends on map, safety, and
offboard command objects because its job is integration.

Bad coupling avoided: perception code does not directly control actuation.

Rebuild challenge: draw the architecture and label which arrows are data flow
and which arrows are command flow.

## Stage 4 - Repository Structure

```text
cad/solidworks/       SolidWorks macro and payload parameters
docs/                 Requirements, trace, critique, teaching, runbooks
ros2_ws/              ROS 2 package and Gazebo launch integration
scripts/              Reproducible demos, conversions, checks, training entry points
simulation/gazebo/    Standalone SDF worlds
src/facade_uav/       Testable Python core
```

Why not put everything in one folder? Because each folder has a different
runtime owner:

- CAD runs in SolidWorks on Windows.
- Python core runs in normal Python/WSL.
- ROS package runs inside ROS 2.
- Gazebo worlds are consumed by Gazebo/ROS launch.
- Docs are human-facing evidence.

If the project grew 100x larger:

- `src/facade_uav/perception` would split into model backends and fusion.
- `src/facade_uav/planning` would split into classical, RL, and optimization.
- `ros2_ws` would gain message definitions and launch profiles.
- `simulation` would gain multiple building worlds and weather cases.
- `cad` would gain assemblies, exports, and manufacturing drawings.

Rebuild challenge: recreate the folder tree on paper and write one sentence for
why each folder exists.

## Stage 5 - File-By-File Walkthrough

This stage focuses on important engineering files. Documentation files are
evidence; source/scripts are behavior.

| File | Why it exists | Inputs | Outputs | Failure modes |
|---|---|---|---|---|
| `src/facade_uav/cleaning_zone_map.py` | Shared grid state for facade panels | Surface, dirt, depth, object flags | Dirty cells, summaries, blocked cells | Bad clean/skip classification affects every downstream step |
| `src/facade_uav/safety_layer.py` | Independent safety shield | `MissionState`, proposed command | allow/hold/abort/return-to-base decision | Incorrect thresholds can stop good missions or allow unsafe ones |
| `src/facade_uav/planning/coverage_path.py` | Greedy and obstacle-aware route logic | `CleaningZoneMap`, start, threshold, clearance | route steps, skipped targets | No route, over-conservative clearance, wrong skipped targets |
| `src/facade_uav/integration/closed_loop.py` | Connect route to safety, command, actuation | route, map, safety bounds | event log and metrics | Resource accounting mismatch, safety bypass |
| `src/facade_uav/perception/opencv_cleaning_zone.py` | Deterministic perception baseline | image file | cleaning-zone map and render | Lighting/texture heuristics misclassify |
| `src/facade_uav/perception/object_identification.py` | Convert map/detections into objects | zone map, YOLO boxes | object records | Low-confidence detections used as truth |
| `src/facade_uav/rl/coverage_env.py` | Test RL planning as a coverage problem | action | observation, reward, done, info | Reward hacking, poor observation, unsafe policy |
| `src/facade_uav/mechanical/quadcopter_payload.py` | Mechanical mass/CG/thrust model | payload parameters | mass budget | Unrealistic motor/payload assumptions |
| `scripts/run_all_verification.sh` | One command to prove the project still works | repo state | pass/fail output | Environment mismatch |
| `scripts/run_closed_loop_mission_demo.py` | End-to-end software loop demo | synthetic fused map | mission logs | Demo data too easy or too fake |
| `scripts/generate_solidworks_quadcopter.py` | CAD dry-run and SolidWorks helper | parameter JSON | mass budget JSON | SolidWorks absent, pywin32 absent |
| `scripts/check_interview_demo_assets.py` | Validate CAD/world demo assets | macro, SDF, parameters | asset check JSON | Missing model names or payload tokens |
| `cad/solidworks/facade_cleaning_quadcopter_generator.vba` | Generate interview CAD model | hard-coded param constants | SolidWorks part | API/template mismatch in SolidWorks |
| `simulation/gazebo/interview_facade_cleaning_world.sdf` | Visual interview world | SDF | Gazebo world | Invalid SDF, misleading static model |
| `ros2_ws/src/facade_cleaning_uav/launch/interview_demo.launch.py` | Launch demo world and status nodes | ROS 2 environment | Gazebo plus ROS nodes | Missing installed world or ROS dependency |

Refactoring opportunities:

- Move repeated demo-map construction into a shared fixture.
- Add typed schemas for JSON outputs.
- Replace static Gazebo UAV visual with dynamic PX4 model.
- Add CI once the environment is stable.

Rebuild challenge: pick any five files and explain who calls them, what they
return, and how they fail.

## Stage 6 - Function-By-Function

### `CleaningZoneMap.mark_object`

Purpose: mark one grid cell as an object with confidence and risk.

Inputs: x, z, object type, confidence, risk level.

Outputs: mutated cell state.

State changes: blocked objects become obstacles, frame surface, and not dirty.

Edge case: a caution object should not become an obstacle.

### `CleaningZoneMap.blocked_cells`

Purpose: return blocked cells inflated by a clearance radius.

Complexity: O(width * height * clearance^2).

Why this implementation: grid is small, simple loops are easier to audit than a
spatial index.

### `find_grid_route`

Purpose: BFS route from start to goal while avoiding blocked cells.

Why BFS: grid moves have equal cost, so BFS gives shortest path in step count.

Edge case: if the goal is inside inflated clearance, return no route by default.

### `plan_obstacle_aware_cleaning_route`

Purpose: repeatedly choose reachable dirty cells and emit transit/clean steps.

Trade-off: greedy selection is not globally optimal, but it is deterministic and
easy to debug.

### `validate_route_clearance`

Purpose: fail loudly if any route step enters inflated blocked cells.

Why it exists: route visualization can look safe while a grid step is actually
inside a clearance zone.

### `SafetyLayer.evaluate`

Purpose: independent decision about whether a proposed command may execute.

Order matters: wind abort and LiDAR validity are checked before normal mission
resource checks.

### `execute_closed_loop_route`

Purpose: turn route steps into safety-checked velocity commands and actuation
events.

Important invariant: water-jet actuation only occurs after safety approval.

### `build_zone_map_from_image`

Purpose: OpenCV baseline that estimates glass, concrete, frames, and dirt.

Important risk: it is heuristic, so it is trusted only as a baseline demo.

### `FacadeCoverageEnv.step`

Purpose: simulate one coverage-planning action with reward terms.

Important risk: bad reward weights can teach the wrong behavior.

### `estimate_mass_budget`

Purpose: compute dry mass, water mass, wet mass, thrust-to-weight, and CG.

Important invariant: thrust-to-weight should be above the demo threshold and CG
offset should stay within limit.

Rebuild challenge: write pseudocode for `SafetyLayer.evaluate` and
`find_grid_route` without opening the files.

## Stage 7 - Data Flow

### Perception data flow

```text
image file
  -> OpenCV patch analysis
  -> cell surface type
  -> dirty confidence
  -> CleaningZoneMap
  -> rendered zone map + cleaning path JSON
```

Failure path: if image reading fails, the analyzer raises a file error. If
surface classification is wrong, later planning still behaves consistently, but
it plans from bad data.

### Object and route data flow

```text
CleaningZoneMap
  -> identified object list
  -> blocked cells with clearance
  -> BFS route
  -> transit/clean steps
  -> skipped targets
```

### Closed-loop data flow

```text
route step
  -> MissionState
  -> proposed velocity command
  -> SafetyLayer decision
  -> event log
  -> water/battery accounting
```

### CAD/simulation data flow

```text
payload parameter JSON
  -> mass budget
  -> SolidWorks macro assumptions
  -> Gazebo visual model
  -> interview storyboard
```

Rebuild challenge: trace one dirty cell from image analysis to water-jet
actuation log.

## Stage 8 - Execution Flow

### Full verification launch

```text
PowerShell script
  -> WSL Ubuntu-22.04-LTS
  -> scripts/run_all_verification.sh
  -> smoke tests
  -> CAD dry-run
  -> perception demos
  -> route and closed-loop demos
  -> safety fault demo
  -> RL evaluation
  -> SDF validation
  -> teaching doc check
  -> ROS build
```

### Closed-loop mission launch

```text
scripts/run_closed_loop_mission_demo.py
  -> build_fused_perception_demo_map
  -> identify_objects_from_zone_map
  -> plan_obstacle_aware_cleaning_route
  -> validate_route_clearance
  -> execute_closed_loop_route
  -> write summary JSON
```

### ROS interview launch

```text
ros2 launch facade_cleaning_uav interview_demo.launch.py
  -> sim.launch.py with interview SDF
  -> safety_node
  -> planner_node
  -> interview_demo_node timeline publisher
```

Rebuild challenge: explain what runs first when you execute the full
PowerShell verification command.

## Stage 9 - Libraries

| Library/tool | Why used | Alternative | When not to use |
|---|---|---|---|
| OpenCV | Fast deterministic image baseline | scikit-image, PIL | When learned segmentation is validated and required |
| NumPy | Array operations | pure Python lists | Very small data only |
| Gymnasium | RL environment interface | custom API | If no RL training/evaluation is needed |
| Stable-Baselines3 | PPO implementation | RLlib, CleanRL | If you cannot justify RL or evaluate it |
| Torch | Deep learning backend | TensorFlow, JAX | If model inference/training is not used |
| Ultralytics | YOLO training/inference wrapper | Detectron2, MMDetection | If labels do not support detection well |
| ROS 2 | Robotics node and launch ecosystem | custom sockets, MAVSDK-only | If you only need offline scripts |
| Gazebo | Robot simulation world | Isaac Sim, Webots | If physics/robotics simulation is unnecessary |
| SolidWorks VBA | CAD automation | Python COM, Onshape API | If no Windows SolidWorks install is available |

Rebuild challenge: justify every non-standard dependency in one sentence.

## Stage 10 - Testing

### Test layers

| Test | Command | What it proves | What it does not prove |
|---|---|---|---|
| Core smoke | `python3 scripts/smoke_test_core.py` | Map, planning, safety, closed-loop basics | Real flight |
| CAD dry-run | `python3 scripts/generate_solidworks_quadcopter.py --dry-run` | Mass/CG/thrust assumptions | SolidWorks model opens |
| Asset check | `python3 scripts/check_interview_demo_assets.py` | Required CAD/world features exist | Visual beauty or physics |
| Perception demo | `python3 scripts/run_perception_demo.py` | OpenCV pipeline works | Production segmentation accuracy |
| Closed-loop demo | `python3 scripts/run_closed_loop_mission_demo.py` | Route to safety to actuation log | PX4 SITL flight |
| RL evaluation | `python3 scripts/evaluate_rl.py` | PPO compared honestly | PPO is good |
| SDF validation | `gz sdf -k ...` | SDF syntax is valid | Scene looks perfect |
| ROS build | `colcon build` | Package installs/builds | Nodes behave correctly for long missions |

Correctness is not "the program runs." Correctness means invariants hold:

- No route clearance violations.
- Safety rejects known unsafe states.
- Dirty glass is cleaned, skip zones are not.
- CAD lift margin passes.
- Generated worlds validate.

Rebuild challenge: write three invariants for the planner and two for the CAD
payload.

## Stage 11 - Debugging

| Symptom | Likely root cause | Isolation method | Fix |
|---|---|---|---|
| No dirty cells found | Perception threshold too strict | Print zone map summary | Tune thresholds or inspect image |
| Route has no clean steps | Targets inside clearance or disconnected map | Inspect `skipped_targets` | Reduce clearance or improve target selection |
| Clearance violation | Planner allowed blocked cell | Run `validate_route_clearance` | Fix blocked-cell logic |
| Safety always holds | Bad standoff/depth defaults | Log `MissionState` | Fix depth/standoff values |
| PPO poor reward | Observation/reward mismatch | Compare reward terms | Redesign observation/curriculum |
| YOLO no boxes | Labels/model not learning | Overfit tiny dataset | Redesign labels or segmentation approach |
| SDF invalid | XML/model geometry error | `gz sdf -k` | Fix SDF syntax |
| ROS build fails | package/setup/launch issue | `colcon build` logs | Fix package data or imports |
| CAD dry-run fails | Bad mass/thrust/CG assumption | Read `validation_issues` | Refine mechanical parameters |

Senior debugging order:

```text
reproduce -> reduce -> inspect inputs -> assert invariants -> compare expected
vs actual -> fix smallest cause -> add regression check
```

Rebuild challenge: choose one failure and write a five-step debugging plan.

## Stage 12 - Production Readiness

Current project status: interview-demo and simulation scaffold, not production.

Missing production pieces:

- Real sensor calibration.
- Dynamic PX4 SITL flight and controller tuning.
- Hardware-in-the-loop tests.
- Real building dataset and model validation.
- CI pipeline for Python and ROS.
- Runtime logging/metrics.
- Safety case and regulatory analysis.
- Operator UI and emergency procedures.
- Versioned model artifacts.
- Deployment scripts.

Configuration management needed:

- YAML for safety thresholds.
- Versioned world files.
- Versioned model checkpoints.
- Recorded mission logs.
- Calibration files for cameras/LiDAR.

Rebuild challenge: list five things that must happen before real hardware
testing.

## Stage 13 - Engineering Review

### Strengths

- Clear separation of map, perception, planning, safety, integration, and CAD.
- Verification script catches many regressions.
- Honest PPO and YOLO limitations.
- Interview world makes the concept visible.
- Mechanical dry-run prevents absurd payload claims.

### Weaknesses

- Gazebo UAV model is visual/static, not a dynamic PX4 vehicle.
- OpenCV perception is heuristic.
- PPO does not beat baseline.
- YOLO obstacle detector failed overfit diagnostic.
- JSON outputs do not have formal schemas yet.
- Some demo data is synthetic and hand-constructed.

### Priority refactors

| Priority | Refactor | Why |
|---|---|---|
| P0 | PX4 dynamic model integration | Biggest gap between demo and real robotics |
| P1 | Typed JSON schemas | Prevent brittle script contracts |
| P1 | Shared demo map fixtures | Avoid duplicated scenario setup |
| P2 | Model evaluation dashboard | Make learned perception progress measurable |
| P2 | CI split for Windows/WSL | Make verification repeatable |

Rebuild challenge: defend why PPO is not claimed as a success yet.

## Stage 14 - Rebuild Roadmap

| Milestone | Goal | Knowledge required | Implementation task | Verification | Common mistake | Interview question |
|---|---|---|---|---|---|---|
| R0 | Problem and requirements | Facade cleaning domain | Write requirements doc | Peer explains it back | Starting with code | Why is this problem hard? |
| R1 | Map model | Grid state design | Implement `CleaningZoneMap` | Dirty/blocked summaries pass | Mixing pixels with planner state | Why not plan on raw image? |
| R2 | Safety layer | Robotics safety gates | Implement `SafetyLayer` | Fault cases reject commands | Trusting planner for safety | Why independent safety? |
| R3 | Planner | BFS and greedy search | Implement route planner | Zero clearance violations | Cleaning inside obstacle clearance | Why BFS? |
| R4 | Perception baseline | OpenCV basics | Image to map | Zone map visual looks coherent | Claiming heuristic is AI | Why baseline first? |
| R5 | Closed-loop log | Control flow | Route to safety to actuation | Nominal and fault logs pass | Actuating before safety | Where can command be blocked? |
| R6 | CAD payload | Mass/CG/thrust | Payload spec and macro | Dry-run passes | Unrealistic lift margin | How much water can it carry? |
| R7 | Gazebo world | SDF/ROS launch | Interview world | SDF valid and ROS builds | Pretty world with no test | What does the world prove? |
| R8 | Learned perception | Segmentation/detection | Train/evaluate models | Held-out metrics improve | Trusting low-confidence boxes | Why did YOLO fail? |
| R9 | RL | PPO and baselines | Train curriculum | Beats greedy/lawnmower | Reward hacking | Why PPO? |
| R10 | PX4 SITL | Offboard control | Dynamic flight demo | Takeoff, standoff, clean, abort | Skipping controller tuning | What breaks near a wall? |

## Concept 1 - Cleaning-Zone Map

### 1. THE PROBLEM

Raw images are not useful to a route planner. A planner needs a compact state:
which facade cells are glass, dirty, blocked, already cleaned, risky, or too
close.

If nobody solves this, the drone might clean concrete, ignore dirty glass, or
fly into protrusions.

### 2. THE NAIVE SOLUTION

A beginner may store a list of image pixels or bounding boxes and plan directly
from them.

It seems reasonable because perception outputs pixels and boxes.

It fails because route planning needs consistent grid semantics, not mixed raw
model outputs.

### 3. THE ENGINEERING SOLUTION

Use `CleaningZoneMap` as a shared intermediate representation.

Trade-off: a grid loses pixel-level detail, but gains planner simplicity,
debuggability, and testability.

Another design would be better if the drone needed millimeter-accurate spray
control.

### 4. MINIMAL EXAMPLE

```python
grid = [
    ["glass_dirty", "glass_clean"],
    ["frame_blocked", "concrete_skip"],
]
```

The planner should target only `glass_dirty`.

### 5. IN MY PROJECT

File: `src/facade_uav/cleaning_zone_map.py`

Classes:

- `PanelCell`
- `CleaningZoneMap`

Important variables:

- `dirty_confidence`
- `surface_type`
- `obstacle`
- `risk_level`
- `depth_m`

Inputs: perception classifications, object detections, depth values.

Outputs: dirty cells, blocked cells, object summaries, plan targets.

### 6. COMMON AI-GENERATED MISTAKES

- Duplicate state: dirty in one list, blocked in another unsynchronized list.
- Wrong assumptions: treating every non-obstacle as cleanable.
- Dead code: fields like depth added but never consumed.
- Bad naming: "wall" when the system needs "glass", "frame", "concrete".
- Fake error handling: silently ignoring out-of-bounds cells.

Detect them with summary assertions and out-of-bounds tests.

### 7. DEBUGGING

Inspect:

- `zone_map.summary()`
- `dirty_cells()`
- `blocked_cells(clearance_cells=1)`

Add assertions:

- A blocked cell cannot remain dirty.
- Concrete cannot be cleanable.
- Cleaned cells cannot remain dirty.

### 8. INTERVIEW DEFENSE

Why not plan directly from YOLO boxes?

Because boxes do not represent clean/skip state, already-cleaned state, depth,
or per-cell route occupancy. A grid map gives the planner a stable contract.

### 9. REBUILD CHALLENGE

Build a 4x3 grid class from memory with:

- `set_dirty`
- `mark_object`
- `dirty_cells`
- `blocked_cells`
- `summary`

## Concept 2 - Independent Safety Layer

### 1. THE PROBLEM

Coverage planners optimize task completion. Safety systems prevent unacceptable
actions. Those are different responsibilities.

If nobody separates them, a learned policy or buggy route planner can become the
only thing preventing collision.

### 2. THE NAIVE SOLUTION

Put penalties in the RL reward and hope the agent learns safety.

It fails because learning is probabilistic and may behave badly outside the
training distribution.

### 3. THE ENGINEERING SOLUTION

Use `SafetyLayer.evaluate` as a hard gate after planning and before actuation.

Trade-off: it can stop missions that might have recovered, but it prevents
unsafe command execution.

### 4. MINIMAL EXAMPLE

```python
if wind_mps > 8:
    return "abort"
if standoff_m < 1:
    return "hold"
return "continue"
```

### 5. IN MY PROJECT

File: `src/facade_uav/safety_layer.py`

Inputs:

- `MissionState`
- proposed command dict

Outputs:

- `SafetyDecision(allowed, action, reason, command)`

Dependencies:

- `SafetyBounds`

### 6. COMMON AI-GENERATED MISTAKES

- Checking battery before collision-critical standoff.
- Returning `allowed=True` with an abort reason.
- Mutating safety bounds during evaluation.
- Hard-coding thresholds in multiple files.
- Treating invalid LiDAR as safe.

Detect with fault-case tests.

### 7. DEBUGGING

Log the full `MissionState` and decision.

Classify failure:

- Data: wrong standoff value.
- Logic: threshold comparison wrong.
- Configuration: bad safety bounds.
- Hardware: LiDAR invalid.
- Environment: high wind.

### 8. INTERVIEW DEFENSE

Why is safety not inside the planner?

Because safety must remain valid even if the planner is replaced, retrained, or
buggy.

### 9. REBUILD CHALLENGE

Write the safety decision tree from memory. Include wind, LiDAR, standoff,
geofence, reservoir, and battery.

## Concept 3 - Obstacle-Aware Route Planning

### 1. THE PROBLEM

A dirty glass target may be near an AC unit, ledge, open window, or frame. The
drone must not fly through that blocked clearance just because the glass is
dirty.

### 2. THE NAIVE SOLUTION

Visit dirty cells in nearest-neighbor order and ignore obstacles.

It seems efficient, but it fails when the nearest target is unsafe or separated
by an obstacle.

### 3. THE ENGINEERING SOLUTION

Inflate blocked cells by a clearance radius and use BFS for grid routes.

Trade-off: conservative clearance can skip some dirty targets, but that is
correct for safety.

### 4. MINIMAL EXAMPLE

```text
S . X T
. . X .
. . . .
```

With clearance, `T` may become unreachable and should be skipped.

### 5. IN MY PROJECT

File: `src/facade_uav/planning/coverage_path.py`

Functions:

- `find_grid_route`
- `plan_obstacle_aware_cleaning_route`
- `validate_route_clearance`

Outputs:

- `steps`
- `skipped_targets`
- `object_summary`

### 6. COMMON AI-GENERATED MISTAKES

- Allowing the goal inside inflated clearance by accident.
- Checking transit steps but not clean steps.
- Forgetting to remove unreachable targets.
- Returning an empty route without reason.
- Using diagonal moves without checking corner collisions.

Detect with a small obstacle map and explicit skipped-target assertions.

### 7. DEBUGGING

Print:

- current cell
- candidate targets
- blocked cells
- chosen route
- skipped targets

If route is empty, check whether the target is inside clearance.

### 8. INTERVIEW DEFENSE

Why BFS and not A*?

BFS is enough for small equal-cost grids and is easier to audit. A* would be
reasonable for larger maps or weighted costs.

### 9. REBUILD CHALLENGE

Draw a 5x5 grid with one obstacle, inflate it by one cell, and hand-compute a
safe route.

## Concept 4 - Closed-Loop Executor

### 1. THE PROBLEM

A route is not a mission. A mission needs commands, safety checks, resource
updates, and actuation decisions.

### 2. THE NAIVE SOLUTION

Write the route to JSON and claim the drone can fly it.

This fails because no one proves commands are safe or that cleaning happens only
after safety approval.

### 3. THE ENGINEERING SOLUTION

Use a closed-loop executor that turns each route step into:

```text
MissionState -> proposed command -> safety decision -> actuation/resource log
```

Trade-off: it is still not real PX4 flight, but it proves the software contract.

### 4. MINIMAL EXAMPLE

```python
for step in route:
    decision = safety.evaluate(state, command)
    if not decision.allowed:
        break
    if step.action == "clean":
        water -= 0.06
```

### 5. IN MY PROJECT

File: `src/facade_uav/integration/closed_loop.py`

Function:

- `execute_closed_loop_route`

Inputs:

- `CleaningZoneMap`
- route dict
- optional safety bounds
- executor config

Outputs:

- event log
- clean/transit counts
- safety override count
- reservoir/battery remaining

### 6. COMMON AI-GENERATED MISTAKES

- Actuating before safety.
- Updating battery on blocked commands.
- Ignoring reservoir depletion.
- Hiding why a mission stopped.
- No fault injection.

Detect by checking nominal and injected-gust outputs.

### 7. DEBUGGING

Inspect `outputs/closed_loop_mission/nominal_execution.json` and
`fault_execution.json`.

Trace the first failed event. Check command, state, safety decision, and action.

### 8. INTERVIEW DEFENSE

Why log actuation instead of controlling hardware now?

Because the project is simulation-first. The log proves the control contract
before hardware or PX4 integration is safe to attempt.

### 9. REBUILD CHALLENGE

Write a mini executor that stops on high wind and only cleans after safety
approval.

## Concept 5 - Mechanical Payload

### 1. THE PROBLEM

A cleaning drone is not just a quadcopter. It carries water, pump, blower,
nozzle, hoses, sensors, and possibly changing mass.

If nobody checks mass and CG, the design can look impressive but be physically
unreasonable.

### 2. THE NAIVE SOLUTION

Draw a drone and attach a tank visually.

It seems convincing in a screenshot, but fails when asked about thrust margin or
center of gravity.

### 3. THE ENGINEERING SOLUTION

Keep a parameterized payload spec and dry-run mass budget before SolidWorks.

Trade-off: the model is approximate, but it catches bad assumptions early.

### 4. MINIMAL EXAMPLE

```python
wet_mass = dry_mass + water_liters
twr = max_thrust_n / (wet_mass * 9.81)
assert twr > 1.5
```

### 5. IN MY PROJECT

Files:

- `src/facade_uav/mechanical/quadcopter_payload.py`
- `scripts/generate_solidworks_quadcopter.py`
- `cad/solidworks/facade_cleaning_quadcopter_generator.vba`

Inputs:

- `cad/solidworks/quadcopter_payload_parameters.json`

Outputs:

- `outputs/cad/quadcopter_payload_spec.json`
- SolidWorks-generated part when macro is run.

### 6. COMMON AI-GENERATED MISTAKES

- Impossible payload mass.
- No CG reasoning.
- No reservoir depletion story.
- CAD not tied to simulation.
- Motor thrust assumed without margin.

Detect with mass budget checks.

### 7. DEBUGGING

If dry-run fails:

- Read `validation_issues`.
- Check wet mass.
- Check thrust-to-weight.
- Check `cg_y_m`.
- Adjust reservoir, battery, payload offsets, or motor thrust.

### 8. INTERVIEW DEFENSE

Why did the first motor choice change?

Because the dry-run showed thrust-to-weight `1.116`, which is too weak for a
credible payload UAV. The design was refined to `1.747`.

### 9. REBUILD CHALLENGE

Recompute wet mass and thrust-to-weight by hand from the parameter JSON.

## Concept 6 - Gazebo Interview World

### 1. THE PROBLEM

A project that only shows JSON logs is hard for interviewers to visualize. They
need to see the environment, drone, refill station, targets, skip zones, and
obstacles.

### 2. THE NAIVE SOLUTION

Use a blank Gazebo world and say the facade is "conceptual."

This fails because the demo does not communicate the actual cleaning mission.

### 3. THE ENGINEERING SOLUTION

Create an interview SDF world with visible mission objects and validate it with
Gazebo.

Trade-off: the current UAV visual model is static. It proves scene/story, not
dynamic flight.

### 4. MINIMAL EXAMPLE

```xml
<model name="dirty_target_patches">
  <static>true</static>
  ...
</model>
```

### 5. IN MY PROJECT

Files:

- `simulation/gazebo/interview_facade_cleaning_world.sdf`
- `ros2_ws/src/facade_cleaning_uav/worlds/interview_facade_cleaning_world.sdf`
- `ros2_ws/src/facade_cleaning_uav/launch/interview_demo.launch.py`

Validation:

- `gz sdf -k ...`
- `scripts/check_interview_demo_assets.py`

### 6. COMMON AI-GENERATED MISTAKES

- Invalid SDF tags.
- World file exists but is not installed in ROS package.
- Visual scene has no mission story.
- Two copies of a world drift apart.
- Claims dynamic flight when model is static.

Detect with SDF validation and asset model-name checks.

### 7. DEBUGGING

If Gazebo fails:

- Run `gz sdf -k`.
- Check XML around the failing line.
- Confirm model names in the asset checker.
- Confirm `setup.py` installs the world file.

### 8. INTERVIEW DEFENSE

What does this world prove?

It proves the scenario and demo environment are represented. It does not yet
prove PX4 dynamic cleaning flight.

### 9. REBUILD CHALLENGE

Create a minimal SDF with ground, wall, dirty patch, obstacle, and UAV visual.

## Concept 7 - RL And Baselines

### 1. THE PROBLEM

Coverage planning can be optimized by learning, but RL can also produce weak or
unsafe behavior if reward, observation, or training curriculum is poor.

### 2. THE NAIVE SOLUTION

Train PPO once and claim it is intelligent.

It fails if it cannot beat a simple deterministic baseline.

### 3. THE ENGINEERING SOLUTION

Keep deterministic baselines and only claim RL success after held-out
comparison.

Trade-off: this is less flashy, but much more defensible.

### 4. MINIMAL EXAMPLE

```text
Baseline reward: 802
PPO reward: -370
Decision: do not claim PPO success.
```

### 5. IN MY PROJECT

Files:

- `src/facade_uav/rl/coverage_env.py`
- `src/facade_uav/rl/evaluate.py`
- `scripts/evaluate_rl.py`
- `scripts/train_ppo_smoke.py`

Outputs:

- `outputs/rl/evaluation.json`

### 6. COMMON AI-GENERATED MISTAKES

- Reporting training reward but not held-out evaluation.
- Comparing against no baseline.
- Ignoring reward-term dominance.
- Claiming "RL" when deterministic fallback is used.
- No seed control.

Detect by reading evaluation JSON and comparing policies.

### 7. DEBUGGING

Inspect:

- reward terms
- coverage ratio
- terminal reason
- reservoir depletion
- nearest-dirty observations

If PPO fails, simplify curriculum before adding complexity.

### 8. INTERVIEW DEFENSE

Why include PPO if it is not final?

Because it is part of the research roadmap, but the current system uses the
trusted deterministic planner until PPO passes the gate.

### 9. REBUILD CHALLENGE

Write a tiny grid-world reward function and explain how it could be gamed.

