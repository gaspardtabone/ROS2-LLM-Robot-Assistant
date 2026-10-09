import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from robot_interfaces.msg import TaskPlan, MissionReport, StepResult
from robot_interfaces.srv import QueryRoomPose
from robot_interfaces.action import SearchObject
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped

class TaskPlannerNode(Node):
    def __init__(self):
        super().__init__('task_planner_node')

        self.sub_plan = self.create_subscription(
            TaskPlan,
            '/task_plan',
            self.plan_callback,
            10
        )

        self.pub_report = self.create_publisher(
            MissionReport,
            '/mission_report',
            10
        )

        self.client_query_room = self.create_client(QueryRoomPose, '/memory/query_room_pose')
        self.nav_action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.search_action_client = ActionClient(self, SearchObject, 'search_object')

        self.get_logger().info("Task Planner Node (FSM) initialized.")

    def plan_callback(self, msg: TaskPlan):
        self.get_logger().info(f"Received new plan with {len(msg.actions)} actions for: '{msg.raw_command}'")
        self.execute_plan(msg)

    def execute_plan(self, plan: TaskPlan):
        report = MissionReport()
        report.raw_command = plan.raw_command
        overall_success = True

        for act in plan.actions:
            step = StepResult()
            step.action_type = act.action_type
            step.details = f"Params: {act.params}"

            if act.action_type == "go_to":
                room_name = act.params[0] if act.params else "dock"
                success = self.execute_go_to(room_name)
                step.success = success
                if not success:
                    overall_success = False
                    report.step_results.append(step)
                    break

            elif act.action_type == "search":
                label = act.params[0] if act.params else "bottle"
                success = self.execute_search(label)
                step.success = success
                if not success:
                    overall_success = False

            elif act.action_type == "return_home":
                success = self.execute_go_to("dock")
                step.success = success

            else:
                step.success = True

            report.step_results.append(step)

        report.success = overall_success
        self.pub_report.publish(report)
        self.get_logger().info(f"Mission complete. Overall success: {overall_success}")

    def execute_go_to(self, room_name: str) -> bool:
        self.get_logger().info(f"Executing go_to('{room_name}')...")
        if not self.client_query_room.wait_for_service(timeout_sec=2.0):
            self.get_logger().warn("QueryRoomPose service not available. Using fallback pose.")
            pose = PoseStamped()
            pose.header.frame_id = 'map'
            pose.pose.position.x = 0.0
            pose.pose.position.y = 0.0
        else:
            req = QueryRoomPose.Request()
            req.room_name = room_name
            future = self.client_query_room.call_async(req)
            rclpy.spin_until_future_complete(self, future, timeout_sec=3.0)
            res = future.result()
            if res and res.found:
                pose = res.pose
            else:
                self.get_logger().error(f"Room '{room_name}' unknown in memory.")
                return False

        if not self.nav_action_client.wait_for_server(timeout_sec=2.0):
            self.get_logger().warn("Nav2 NavigateToPose action server offline. Simulating arrival.")
            return True

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = pose
        send_future = self.nav_action_client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, send_future, timeout_sec=5.0)
        goal_handle = send_future.result()

        if not goal_handle or not goal_handle.accepted:
            self.get_logger().error("Nav2 goal rejected.")
            return False

        res_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, res_future, timeout_sec=60.0)
        return True

    def execute_search(self, label: str) -> bool:
        self.get_logger().info(f"Executing search('{label}')...")
        if not self.search_action_client.wait_for_server(timeout_sec=2.0):
            self.get_logger().warn("SearchObject action server offline. Simulating success.")
            return True

        goal_msg = SearchObject.Goal()
        goal_msg.label = label
        send_future = self.search_action_client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, send_future, timeout_sec=5.0)
        goal_handle = send_future.result()

        if not goal_handle or not goal_handle.accepted:
            return False

        res_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, res_future, timeout_sec=15.0)
        result = res_future.result()
        return result.result.found if result else False


def main(args=None):
    rclpy.init(args=args)
    node = TaskPlannerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
