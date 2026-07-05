#!/usr/bin/env bash
set -u

echo "Facade UAV ROS/Gazebo compatibility audit"
echo "========================================"

echo
echo "OS:"
grep PRETTY_NAME /etc/os-release || true

echo
echo "Core tools:"
for tool in python3 pip3 git make cmake ros2 colcon gz ign gazebo; do
  found="$(command -v "$tool" || true)"
  printf "%-10s %s\n" "$tool" "${found:-missing}"
done

echo
echo "ROS:"
if [ -f /opt/ros/humble/setup.bash ]; then
  set +u
  # shellcheck disable=SC1091
  source /opt/ros/humble/setup.bash
  set -u
  echo "ROS_DISTRO=${ROS_DISTRO:-unset}"
  ros2 --help >/dev/null && echo "ros2 CLI OK"
else
  echo "/opt/ros/humble/setup.bash missing"
fi

echo
echo "Gazebo CLI:"
gz --versions 2>/dev/null || true
gz sim --versions 2>/dev/null || true
if command -v ign >/dev/null 2>&1; then
  ign gazebo --versions 2>/dev/null || true
fi

echo
echo "Important apt packages:"
dpkg -l \
  | grep '^ii' \
  | grep -E 'ros-humble-ros-gz|ros-humble-desktop|gz-harmonic|gz-fortress|libignition-gazebo6|python3-colcon-common-extensions|micro-xrce|px4' \
  | sed -E 's/[[:space:]]+/ /g' \
  | cut -d' ' -f2,3 \
  | sort || true

echo
echo "Apt candidates:"
apt-cache policy \
  ros-humble-ros-gz \
  ros-humble-ros-gz-bridge \
  ros-humble-ros-gz-sim \
  python3-colcon-common-extensions \
  gz-harmonic \
  gz-fortress 2>/dev/null || true

echo
echo "Project workspace:"
PROJECT_ROOT="/mnt/c/Users/mohit/OneDrive/Documents/Facade_drone_Vision"
if [ -d "$PROJECT_ROOT" ]; then
  echo "$PROJECT_ROOT exists"
else
  echo "$PROJECT_ROOT missing"
fi
