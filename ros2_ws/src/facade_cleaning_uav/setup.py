from setuptools import setup

package_name = "facade_cleaning_uav"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", ["launch/facade_cleaning_uav.launch.py"]),
        (f"share/{package_name}/launch", ["launch/sim.launch.py"]),
        (f"share/{package_name}/config", ["config/safety.yaml"]),
        (f"share/{package_name}/config", ["config/bridge.yaml"]),
        (f"share/{package_name}/worlds", ["worlds/facade_world.sdf"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Mohit",
    maintainer_email="mohit@example.com",
    description="ROS 2 integration scaffold for facade-cleaning UAV.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "safety_node = facade_cleaning_uav.safety_node:main",
            "planner_node = facade_cleaning_uav.planner_node:main",
        ],
    },
)
