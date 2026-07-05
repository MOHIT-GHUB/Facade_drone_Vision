#!/usr/bin/env bash
set -euo pipefail

ROOT="/mnt/c/Users/mohit/OneDrive/Documents/Facade_drone_Vision"
cd "$ROOT"

echo "[1/8] Core smoke test"
python3 scripts/smoke_test_core.py

echo "[2/8] Python stack"
PYTHONPATH=src python3 scripts/check_python_stack.py

echo "[3/8] Perception demo"
PYTHONPATH=src python3 scripts/run_perception_demo.py
PYTHONPATH=src python3 scripts/analyze_building_image.py \
  --input outputs/perception_demo/synthetic_facade.png \
  --output-dir outputs/building_analysis

echo "[4/8] Object avoidance and closed-loop mission"
PYTHONPATH=src python3 scripts/demo_object_avoidance_route.py
PYTHONPATH=src python3 scripts/run_closed_loop_mission_demo.py

echo "[5/8] Safety fault demo"
PYTHONPATH=src python3 scripts/safety_fault_demo.py

echo "[6/8] RL evaluation"
PYTHONPATH=src CUDA_VISIBLE_DEVICES= python3 scripts/evaluate_rl.py

echo "[7/8] SDF validation"
gz sdf -k simulation/gazebo/facade_world.sdf
gz sdf -k ros2_ws/src/facade_cleaning_uav/worlds/facade_world.sdf

echo "[8/8] ROS build"
env -i HOME=/home/mohit USER=mohit PATH=/home/mohit/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin bash -lc \
  'source /opt/ros/humble/setup.bash; cd /mnt/c/Users/mohit/OneDrive/Documents/Facade_drone_Vision/ros2_ws; colcon build --symlink-install'

echo "verification complete"
