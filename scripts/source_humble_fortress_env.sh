#!/usr/bin/env bash

# Source this file before building or running ROS 2 nodes:
#   source scripts/source_humble_fortress_env.sh

set -u

if [ ! -f /opt/ros/humble/setup.bash ]; then
  echo "Missing /opt/ros/humble/setup.bash. Install ROS 2 Humble first." >&2
  return 1 2>/dev/null || exit 1
fi

set +u
# shellcheck disable=SC1091
source /opt/ros/humble/setup.bash
set -u

PROJECT_ROOT="/mnt/c/Users/mohit/OneDrive/Documents/Facade_drone_Vision"
if [ -f "$PROJECT_ROOT/ros2_ws/install/setup.bash" ]; then
  set +u
  # shellcheck disable=SC1091
  source "$PROJECT_ROOT/ros2_ws/install/setup.bash"
  set -u
fi

export FACADE_UAV_PROJECT_ROOT="$PROJECT_ROOT"
export FACADE_UAV_ROS_DISTRO="humble"
export FACADE_UAV_GAZEBO_TARGET="fortress"

echo "ROS_DISTRO=${ROS_DISTRO:-unset}"
echo "FACADE_UAV_GAZEBO_TARGET=$FACADE_UAV_GAZEBO_TARGET"
