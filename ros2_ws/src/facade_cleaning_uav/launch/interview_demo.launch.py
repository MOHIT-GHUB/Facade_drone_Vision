from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    return LaunchDescription(
        [
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution(
                        [FindPackageShare("facade_cleaning_uav"), "launch", "sim.launch.py"]
                    )
                ),
                launch_arguments={"world": "interview_facade_cleaning_world.sdf"}.items(),
            ),
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
            Node(
                package="facade_cleaning_uav",
                executable="interview_demo_node",
                name="facade_interview_demo_node",
                output="screen",
            ),
        ]
    )

