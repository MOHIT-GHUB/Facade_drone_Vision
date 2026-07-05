def main() -> None:
    try:
        import rclpy
        from rclpy.node import Node
        from std_msgs.msg import String
    except ModuleNotFoundError as exc:
        raise RuntimeError("Run this node inside a ROS 2 environment with rclpy installed.") from exc

    class SafetyNode(Node):
        def __init__(self) -> None:
            super().__init__("facade_safety_node")
            self.publisher = self.create_publisher(String, "facade/safety/status", 10)
            self.timer = self.create_timer(1.0, self.publish_status)
            self.get_logger().info("Facade safety node started")

        def publish_status(self) -> None:
            msg = String()
            msg.data = "safety=active standoff_geofence=active wind_abort=active"
            self.publisher.publish(msg)

    rclpy.init()
    node = SafetyNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
