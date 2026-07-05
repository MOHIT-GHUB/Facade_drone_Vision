# Environment Report

Generated from the current Codex sandbox on 2026-07-05 IST.

## Windows/Python

- Python is available: `Python 3.13.13`
- `numpy` is not installed.
- `cv2` is not installed.
- `gymnasium` is not installed.
- `stable_baselines3` is not installed.

## WSL/Ubuntu

Updated after user-provided host check:

```text
Ubuntu-22.04-LTS    Stopped    2
docker-desktop      Stopped    2
Ubuntu              Stopped    2
Ubuntu-22.04        Stopped    2
```

`Ubuntu-22.04-LTS` is accessible from Codex now.

Observed inside `Ubuntu-22.04-LTS`:

- Ubuntu 22.04.5 LTS.
- Python 3.10.12.
- ROS Humble exists at `/opt/ros/humble`.
- Gazebo CLI `gz` exists and reports version `8.9.0`.
- `gz-harmonic` is installed.
- `ros-humble-ros-gz` is not installed.
- `python3-colcon-common-extensions` is not installed.
- `sudo` requires the WSL password.

Updated after installation pass:

- `ros-humble-ros-gz` is installed.
- `ros-humble-ros-gz-bridge` is installed.
- `ros-humble-ros-gz-sim` is installed.
- Ignition Gazebo 6 libraries are installed.
- `colcon` is available from `/home/mohit/.local/bin/colcon`.
- `python3.10-venv` is installed.

## What to do without logging out

Use this repo from Windows first:

```powershell
python scripts\smoke_test_core.py
```

Then, from your own normal Windows terminal, check WSL:

```powershell
wsl.exe -l -v
```

If Ubuntu appears there, open it and run:

```bash
cd /mnt/c/Users/mohit/OneDrive/Documents/Facade_drone_Vision
bash scripts/check_environment.sh
```

For the cautious ROS/Gazebo route, follow `docs/07_ros_gazebo_compatibility.md`.
