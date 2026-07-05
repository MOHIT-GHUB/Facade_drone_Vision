# ROS/Gazebo Compatibility Plan

## Current finding

Target distro checked:

`Ubuntu-22.04-LTS`

Observed:

- Ubuntu 22.04.5 LTS.
- ROS Humble exists at `/opt/ros/humble`.
- Gazebo Harmonic is installed: `gz sim` reports `8.9.0`.
- `python3-colcon-common-extensions` is not installed.
- `ros-humble-ros-gz` is not installed.
- `sudo` requires your WSL password, so package installation must be run manually inside Ubuntu.

## Compatibility decision

Use this conservative stack for the project:

- Ubuntu 22.04 LTS
- ROS 2 Humble
- Gazebo Fortress / Ignition Gazebo 6 bridge packages through `ros-humble-ros-gz`
- PX4 added only after the ROS/Gazebo bridge builds cleanly

Why:

- ROS Humble binary `ros_gz` packages are available for Fortress.
- Your installed Harmonic can stay present, but the project should not rely on Harmonic for the first ROS bridge milestone.
- The apt dry-run for `ros-humble-ros-gz python3-colcon-common-extensions` showed `0` removals, so deletion is not needed yet.

Official references:

- Gazebo's ROS installation guide recommends checking ROS/Gazebo version pairing before installing `ros_gz`: https://gazebosim.org/docs/latest/ros_installation/
- ROS Index states Humble `ros_gz` binaries are available for Fortress: https://index.ros.org/r/ros_gz/

## Do not delete yet

Do not delete:

- `Ubuntu-22.04-LTS`
- `Ubuntu`
- `Ubuntu-22.04`
- `docker-desktop`
- Gazebo Harmonic packages

Deletion is only justified if the non-destructive Humble/Fortress bridge route fails repeatedly and the failure is proven to be package-version conflict.

## Manual install route

Inside `Ubuntu-22.04-LTS`:

```bash
cd /mnt/c/Users/mohit/OneDrive/Documents/Facade_drone_Vision
bash scripts/wsl_ros_gazebo_audit.sh
bash scripts/install_humble_fortress_prereqs.sh
source scripts/source_humble_fortress_env.sh
cd ros2_ws
colcon build --symlink-install
```

## If a clean environment becomes necessary

Preferred clean route:

1. Export or back up any important work from existing WSL distros.
2. Create a new dedicated Ubuntu 22.04 WSL distro named something like `FacadeUAV-22.04`.
3. Install only ROS Humble, `ros-humble-ros-gz`, colcon, and project Python dependencies.
4. Keep the existing distros untouched until the new one builds and runs the project.

Do not start by deleting old distros. Keep rollback paths.
