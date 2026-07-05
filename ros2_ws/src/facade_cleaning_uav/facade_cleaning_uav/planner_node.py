def main() -> None:
    try:
        import rclpy
        from rclpy.node import Node
        from std_msgs.msg import String
    except ModuleNotFoundError as exc:
        raise RuntimeError("Run this node inside a ROS 2 environment with rclpy installed.") from exc

    class PlannerNode(Node):
        def __init__(self) -> None:
            super().__init__("facade_planner_node")
            self.publisher = self.create_publisher(String, "facade/planner/status", 10)
            self.timer = self.create_timer(1.0, self.publish_status)
            self.get_logger().info("Facade planner node started with greedy-safe fallback")

        def publish_status(self) -> None:
            msg = String()
            msg.data = "planner=greedy_nearest_dirty_fallback ppo_gate=not_passed"
            self.publisher.publish(msg)

    rclpy.init()
    node = PlannerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
