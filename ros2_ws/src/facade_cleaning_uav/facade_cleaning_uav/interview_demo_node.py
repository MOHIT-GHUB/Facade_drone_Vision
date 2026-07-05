def main() -> None:
    try:
        import rclpy
        from rclpy.node import Node
        from std_msgs.msg import String
    except ModuleNotFoundError as exc:
        raise RuntimeError("Run this node inside a ROS 2 environment with rclpy installed.") from exc

    mission_steps = [
        "01 start_pad: UAV powered on at facade start pad",
        "02 water_connect: quick-connect hose/refill station verified",
        "03 takeoff: climb to safe facade standoff",
        "04 perception: RGB/thermal/LiDAR scan builds cleaning-zone map",
        "05 classification: glass targets kept, concrete/frame/AC units skipped",
        "06 planning: obstacle-aware route generated with clearance",
        "07 safety_gate: wind/standoff/battery/reservoir checks approve command",
        "08 actuation: water jet and blower clean selected glass target",
        "09 fault_demo: injected gust triggers hold/abort safety override",
    ]

    class InterviewDemoNode(Node):
        def __init__(self) -> None:
            super().__init__("facade_interview_demo_node")
            self.publisher = self.create_publisher(String, "facade/demo/status", 10)
            self.index = 0
            self.timer = self.create_timer(1.0, self.publish_step)
            self.get_logger().info("Facade interview demo timeline started")

        def publish_step(self) -> None:
            msg = String()
            msg.data = mission_steps[self.index % len(mission_steps)]
            self.publisher.publish(msg)
            self.index += 1

    rclpy.init()
    node = InterviewDemoNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()

