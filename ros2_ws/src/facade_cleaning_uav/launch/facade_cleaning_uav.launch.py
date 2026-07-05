from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            Node(
                package="facade_cleaning_uav",
                executable="safety_node",
                name="facade_safety_node",
                output="screen",
            ),
            Node(
                package="facade_cleaning_uav",
                executable="planner_node",
                name="facade_planner_node",
                output="screen",
            ),
        ]
    )
