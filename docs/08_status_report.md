# Status Report

Generated on 2026-07-05 IST.

## What is working

- WSL `Ubuntu-22.04-LTS` is usable.
- ROS Humble is installed and sources correctly.
- `ros-humble-ros-gz` is installed.
- Ignition/Fortress Gazebo bridge libraries are installed alongside existing Gazebo Harmonic.
- `colcon` builds the ROS 2 package.
- Gazebo world SDF validates.
- OpenCV synthetic perception demo runs.
- Building-image analysis now separates cleanable glass from concrete/frame/unknown skip zones.
- Cleaning path JSON is generated for dirty cleanable glass only.
- Safety layer fault demo runs.
- Stable-Baselines3 PPO training runs and saves a model.
- Baseline RL evaluation script runs.
- CMP facade dataset is prepared for both cleaning segmentation and obstacle detection.
- SegFormer cleaning inference can produce a cleaning-zone map and path.
- YOLO11n obstacle detector pipeline trains, saves weights, and runs inference.
- Object-aware route planner now enforces inflated obstacle clearance.
- Closed-loop mission demo runs planner steps through safety, velocity command
  generation, and cleaning actuation logs.
- Injected gust fault triggers a safety override in the closed-loop demo.

## Verification results

Latest checked by:

```bash
bash scripts/run_all_verification.sh
```

Latest checked outputs:

- Core smoke test: passed, including closed-loop executor checks.
- Perception demo produced `61` cleanable glass cells, `9` concrete skip cells, `26` frame skip cells, and `58` cleaning waypoints.
- ROS build: `facade_cleaning_uav` finished successfully.
- SDF validation: both world files valid.
- RL:
  - Lawnmower: coverage `0.989`, reward `720.6`, steps `94`.
  - Greedy nearest-dirty: coverage `0.989`, reward `802.1`, steps `98`.
- PPO smoke policy: coverage `0.057`, reward `-370.7`, steps `159`.
- SegFormer staged model: validation pixel accuracy `0.439` on a 120-sample/96px CPU run.
- SegFormer learned pipeline produced `17` cleaning waypoints on sample `cmp_b0001`.
- YOLO obstacle dataset: `516` train images, `90` validation images, `1872` balcony boxes, `4425` blind boxes.
- YOLO11n smoke model: training/inference pipeline verified, but mAP is effectively zero after one fractional CPU epoch.
- Object-avoidance route demo: `14` identified objects, `20` route steps after
  conservative clearance skipping, and `0` clearance violations.
- Closed-loop mission demo:
  - Nominal run: `20` events, `2` safe cleaning events, `0` safety overrides.
  - Fault run: injected gust triggered `1` safety override.
  - Clearance violations: `0`.

## Honest PPO gate

PPO does not yet beat the baseline. Do not claim the PPO result as final.

What changed to improve it:

- Added nearest-dirty features to the observation.
- Added dense target-progress reward.
- Made wind a zero-mean disturbance instead of a guaranteed upward drift.
- Trained a 30k-step smoke policy.

The learning curve improved during training, but held-out evaluation is still poor. The current trusted demo planner is `greedy_nearest_dirty`; PPO remains an M4 research task.

## Demo path today

Use this for a truthful demo:

1. Show synthetic facade and OpenCV cleaning-zone map.
2. Show safety fault overrides.
3. Show Gazebo facade world validation and ROS package build.
4. Show lawnmower vs greedy comparison.
5. Show `outputs/closed_loop_mission/summary.json` to prove the planner is now
   connected to safety, offboard-command shaping, and actuation logging.
6. Explain that PPO training runs but has not passed its baseline gate yet.
7. Explain that SegFormer/YOLO learned perception is wired, with SegFormer staged and YOLO still requiring serious training.

## Next technical move

To make PPO pass:

- Add flattened local map observation or CNN policy.
- Train with curriculum: no obstacles/no wind, then obstacles, then wind.
- Add evaluation callback and save best policy only.
- Compare over at least 20 held-out seeds, not one seed.

To make learned perception stronger:

- Train SegFormer at 256 px or higher on GPU for multiple epochs.
- Train YOLO11n on the full CMP obstacle dataset for more epochs.
- Add more real-world facade obstacle classes: AC units, ropes, pipes, protruding ledges, open windows, people, birds, and temporary maintenance equipment.
- Fuse SegFormer clean/skip masks with YOLO obstacle boxes before path planning.
