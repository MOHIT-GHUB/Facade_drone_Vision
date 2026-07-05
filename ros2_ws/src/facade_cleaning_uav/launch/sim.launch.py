from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    ros_gz_sim = FindPackageShare("ros_gz_sim")
    world_name = LaunchConfiguration("world")
    world = PathJoinSubstitution(
        [FindPackageShare("facade_cleaning_uav"), "worlds", world_name]
    )
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "world",
                default_value="facade_world.sdf",
                description="World SDF file installed in the facade_cleaning_uav package.",
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution([ros_gz_sim, "launch", "gz_sim.launch.py"])
                ),
                launch_arguments={"gz_args": ["-r ", world]}.items(),
            ),
        ]
    )
