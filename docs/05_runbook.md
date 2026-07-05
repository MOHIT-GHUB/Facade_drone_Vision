# Step-by-Step Runbook

## Step 1 - Verify the core code

```powershell
python scripts\smoke_test_core.py
```

This checks:

- cleaning-zone map basics
- safety-layer emergency decisions
- pure-Python coverage environment stepping

## Step 2 - Check local dependencies

```powershell
powershell -ExecutionPolicy Bypass -File scripts\check_environment.ps1
```

## Step 3 - Create Python environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Step 4 - Run PPO smoke training

After dependencies are installed:

```powershell
python -m facade_uav.rl.ppo_trainer --timesteps 2000
```

Before PPO, run the deterministic baseline:

```powershell
python scripts\evaluate_lawnmower.py
```

## Step 5 - Run OpenCV perception on a frame or video

After OpenCV is installed:

```powershell
python -m facade_uav.perception.opencv_cleaning_zone --input path\to\facade.jpg --output outputs\zone_map.png
```

Or run the full synthetic facade perception demo:

```bash
python3 scripts/run_perception_demo.py
```

## Step 6 - ROS 2/Gazebo route

From Ubuntu/WSL when available:

```bash
cd /mnt/c/Users/mohit/OneDrive/Documents/Facade_drone_Vision
bash scripts/wsl_ros_gazebo_audit.sh
bash scripts/install_humble_fortress_prereqs.sh
source scripts/source_humble_fortress_env.sh
cd ros2_ws
colcon build
source install/setup.bash
ros2 launch facade_cleaning_uav facade_cleaning_uav.launch.py
```

To launch the Gazebo facade world through `ros_gz_sim`:

```bash
ros2 launch facade_cleaning_uav sim.launch.py
```

## Step 7 - Update evidence

After each successful run, update:

- `docs/04_milestone_log.md`
- `outputs/` with screenshots, plots, or logs

## Full Verification

From `Ubuntu-22.04-LTS`:

```bash
cd /mnt/c/Users/mohit/OneDrive/Documents/Facade_drone_Vision
bash scripts/run_all_verification.sh
```
