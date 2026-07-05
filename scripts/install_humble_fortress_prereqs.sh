#!/usr/bin/env bash
set -euo pipefail

echo "This installs the conservative ROS Humble + Gazebo Fortress bridge path."
echo "It does not remove Gazebo Harmonic or any WSL distro."
echo

if [ ! -f /opt/ros/humble/setup.bash ]; then
  echo "ROS Humble is not installed at /opt/ros/humble."
  echo "Install ros-humble-desktop first, then rerun this script."
  exit 1
fi

echo "Dry-run first:"
sudo apt-get update
apt-get -s install ros-humble-ros-gz python3-colcon-common-extensions

echo
read -r -p "Proceed with non-destructive install? Type YES: " answer
if [ "$answer" != "YES" ]; then
  echo "Cancelled."
  exit 0
fi

sudo apt-get install -y ros-humble-ros-gz python3-colcon-common-extensions

echo
echo "Installed. Verify with:"
echo "  bash scripts/wsl_ros_gazebo_audit.sh"
echo "  source scripts/source_humble_fortress_env.sh"
echo "  cd ros2_ws && colcon build --symlink-install"
