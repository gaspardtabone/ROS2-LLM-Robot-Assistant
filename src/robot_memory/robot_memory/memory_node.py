import sqlite3
import os
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from robot_interfaces.srv import QueryRoomPose, UpdateObject
import math

class MemoryNode(Node):
    def __init__(self):
        super().__init__('memory_node')

        self.db_path = self.declare_parameter('db_path', 'assistant_memory.db').get_parameter_value().string_value
        self.init_db()

        self.srv_query_room = self.create_service(
            QueryRoomPose,
            '/memory/query_room_pose',
            self.handle_query_room_pose
        )

        self.srv_update_object = self.create_service(
            UpdateObject,
            '/memory/update_object',
            self.handle_update_object
        )

        self.get_logger().info("Memory Node initialized with SQLite database.")

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        schema_path = os.path.join(os.path.dirname(__file__), 'db_schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                cursor.executescript(f.read())
        else:
            cursor.execute("CREATE TABLE IF NOT EXISTS rooms (name TEXT PRIMARY KEY, x REAL, y REAL, yaw REAL);")
            cursor.execute("CREATE TABLE IF NOT EXISTS objects (id INTEGER PRIMARY KEY AUTOINCREMENT, label TEXT, room TEXT, x REAL, y REAL, z REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);")
            cursor.execute("INSERT OR IGNORE INTO rooms (name, x, y, yaw) VALUES ('dock', 0.0, 0.0, 0.0);")
            cursor.execute("INSERT OR IGNORE INTO rooms (name, x, y, yaw) VALUES ('living_room', -1.5, 1.0, 0.0);")
            cursor.execute("INSERT OR IGNORE INTO rooms (name, x, y, yaw) VALUES ('kitchen', 2.0, 2.0, 0.0);")
        conn.commit()
        conn.close()

    def handle_query_room_pose(self, request, response):
        room_name = request.room_name.lower().strip()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT x, y, yaw FROM rooms WHERE name=?", (room_name,))
        row = cursor.fetchone()
        conn.close()

        if row:
            x, y, yaw = row
            pose = PoseStamped()
            pose.header.frame_id = 'map'
            pose.header.stamp = self.get_clock().now().to_msg()
            pose.pose.position.x = float(x)
            pose.pose.position.y = float(y)
            pose.pose.position.z = 0.0

            cy = math.cos(yaw * 0.5)
            sy = math.sin(yaw * 0.5)
            pose.pose.orientation.w = cy
            pose.pose.orientation.z = sy

            response.pose = pose
            response.found = True
            self.get_logger().info(f"QueryRoomPose: '{room_name}' -> x={x}, y={y}")
        else:
            response.found = False
            self.get_logger().warn(f"QueryRoomPose: room '{room_name}' not found.")

        return response

    def handle_update_object(self, request, response):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO objects (label, room, x, y, z) VALUES (?, ?, ?, ?, ?)",
            (request.label, request.room, request.pose.position.x, request.pose.position.y, request.pose.position.z)
        )
        conn.commit()
        conn.close()

        response.success = True
        response.message = f"Saved object '{request.label}' in room '{request.room}'"
        self.get_logger().info(response.message)
        return response


def main(args=None):
    rclpy.init(args=args)
    node = MemoryNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
