#!/usr/bin/env bash
set -u

echo "Facade UAV Ubuntu environment check"
echo "Kernel: $(uname -a)"

echo
echo "Python:"
command -v python3 || true
python3 --version || true

echo
echo "ROS 2:"
command -v ros2 || true
printenv ROS_DISTRO || true

echo
echo "Gazebo:"
command -v gz || true
command -v gazebo || true

echo
echo "PX4:"
command -v px4 || true

echo
echo "Colcon:"
command -v colcon || true
