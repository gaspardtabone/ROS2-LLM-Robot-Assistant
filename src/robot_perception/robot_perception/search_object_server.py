import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from vision_msgs.msg import Detection2DArray
from robot_interfaces.action import SearchObject
from robot_perception.depth_utils import estimate_3d_pose
import time

class SearchObjectActionServer(Node):
    def __init__(self):
        super().__init__('search_object_action_server')

        self._action_server = ActionServer(
            self,
            SearchObject,
            'search_object',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )

        self.latest_detections = None
        self.sub_detections = self.create_subscription(
            Detection2DArray,
            '/detected_objects',
            self.detections_callback,
            10
        )
        self.get_logger().info("SearchObject Action Server initialized.")

    def detections_callback(self, msg: Detection2DArray):
        self.latest_detections = msg

    def goal_callback(self, goal_request):
        self.get_logger().info(f"Received SearchObject goal for label: '{goal_request.label}'")
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info("Received cancel request for SearchObject goal.")
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        target_label = goal_handle.request.label.lower()
        feedback_msg = SearchObject.Feedback()
        result = SearchObject.Result()

        frames_scanned = 0
        max_confidence = 0.0

        start_time = time.time()
        timeout = 10.0  # Seconds to scan

        while (time.time() - start_time) < timeout:
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info("SearchObject goal canceled.")
                result.found = False
                return result

            frames_scanned += 1
            if self.latest_detections is not None:
                for det in self.latest_detections.detections:
                    for hyp in det.results:
                        class_id = hyp.hypothesis.class_id.lower()
                        score = float(hyp.hypothesis.score)
                        if score > max_confidence:
                            max_confidence = score

                        if class_id == target_label or target_label in class_id:
                            self.get_logger().info(f"Target object '{target_label}' found with confidence {score:.2f}!")
                            result.found = True
                            result.pose = estimate_3d_pose(
                                det.bbox.center.position.x,
                                det.bbox.center.position.y
                            )
                            goal_handle.succeed()
                            return result

            feedback_msg.frames_scanned = frames_scanned
            feedback_msg.max_confidence = max_confidence
            goal_handle.publish_feedback(feedback_msg)
            time.sleep(0.2)

        self.get_logger().info(f"Timeout reached. Target object '{target_label}' not found.")
        result.found = False
        goal_handle.succeed()
        return result


def main(args=None):
    rclpy.init(args=args)
    server = SearchObjectActionServer()
    rclpy.spin(server)
    server.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
