import os
import time
import math
import random
import cv2
import numpy as np

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge

class SyntheticDatasetGenerator(Node):
    def __init__(self):
        super().__init__('synthetic_dataset_generator')

        self.declare_parameter('output_dir', 'synthetic_dataset')
        self.declare_parameter('num_samples', 200)
        self.declare_parameter('class_id', 0)
        self.declare_parameter('class_name', 'bottle')

        self.output_dir = self.get_parameter('output_dir').get_parameter_value().string_value
        self.num_samples = self.get_parameter('num_samples').get_parameter_value().integer_value
        self.class_id = self.get_parameter('class_id').get_parameter_value().integer_value
        self.class_name = self.get_parameter('class_name').get_parameter_value().string_value

        self.bridge = CvBridge()
        self.current_image = None
        self.sample_count = 0

        # Setup dataset folder hierarchy
        self.setup_directories()

        # Subscription & Publisher
        self.sub_image = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        self.pub_cmd_vel = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Timer for dataset generation step (every 0.5s)
        self.timer = self.create_timer(0.5, self.generation_step)
        self.get_logger().info(f"Synthetic Dataset Generator Node started. Target samples: {self.num_samples}")

    def setup_directories(self):
        self.train_img_dir = os.path.join(self.output_dir, 'images', 'train')
        self.val_img_dir = os.path.join(self.output_dir, 'images', 'val')
        self.train_lbl_dir = os.path.join(self.output_dir, 'labels', 'train')
        self.val_lbl_dir = os.path.join(self.output_dir, 'labels', 'val')

        for d in [self.train_img_dir, self.val_img_dir, self.train_lbl_dir, self.val_lbl_dir]:
            os.makedirs(d, exist_ok=True)

        # Create dataset.yaml
        yaml_content = f"""path: {os.path.abspath(self.output_dir)}
train: images/train
val: images/val

names:
  {self.class_id}: {self.class_name}
"""
        with open(os.path.join(self.output_dir, 'dataset.yaml'), 'w') as f:
            f.write(yaml_content)

        self.get_logger().info(f"Created dataset structure and dataset.yaml in '{self.output_dir}'")

    def image_callback(self, msg: Image):
        try:
            self.current_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f"CvBridge Error: {e}")

    def generation_step(self):
        if self.current_image is None:
            self.get_logger().warn("Waiting for /camera/image_raw stream...")
            return

        if self.sample_count >= self.num_samples:
            self.stop_robot()
            self.get_logger().info(f"🎉 Dataset generation complete! {self.sample_count} samples saved to '{self.output_dir}'.")
            self.timer.cancel()
            return

        # 1. Drive robot slightly around to vary viewing perspective
        cmd = Twist()
        cmd.linear.x = 0.05
        cmd.angular.z = random.uniform(-0.4, 0.4)
        self.pub_cmd_vel.publish(cmd)

        # 2. Extract synthetic green bottle bounding box via HSV color segmentation
        # (In Gazebo Fortress, the target bottle is green: RGB ~ [0.1, 0.7, 0.2])
        bbox = self.detect_synthetic_target_bbox(self.current_image)

        if bbox is None:
            # Target object not currently visible in camera FOV, keep moving
            return

        # 3. Split 80% train / 20% validation
        is_val = (self.sample_count % 5 == 0)
        img_dir = self.val_img_dir if is_val else self.train_img_dir
        lbl_dir = self.val_lbl_dir if is_val else self.train_lbl_dir

        filename = f"frame_{self.sample_count:04d}"
        img_path = os.path.join(img_dir, f"{filename}.jpg")
        lbl_path = os.path.join(lbl_dir, f"{filename}.txt")

        # Save Image
        cv2.imwrite(img_path, self.current_image)

        # Save YOLO annotation format: <class_id> <x_center> <y_center> <width> <height>
        x_c, y_c, w, h = bbox
        with open(lbl_path, 'w') as f:
            f.write(f"{self.class_id} {x_c:.6f} {y_c:.6f} {w:.6f} {h:.6f}\n")

        self.sample_count += 1
        self.get_logger().info(f"[{self.sample_count}/{self.num_samples}] Saved '{filename}' (bbox: x={x_c:.2f}, y={y_c:.2f}, w={w:.2f}, h={h:.2f})")

    def detect_synthetic_target_bbox(self, img):
        """Segment target object in Gazebo image to extract normalized YOLO bbox."""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # Green bottle HSV range in Gazebo
        lower_green = np.array([35, 50, 50])
        upper_green = np.array([85, 255, 255])

        mask = cv2.inRange(hsv, lower_green, upper_green)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        # Take largest green contour
        c = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(c)
        if area < 100:  # Ignore tiny noise artifacts
            return None

        x, y, w, h = cv2.boundingRect(c)
        img_h, img_w, _ = img.shape

        # Normalize to 0.0 - 1.0 range
        x_center = (x + w / 2.0) / img_w
        y_center = (y + h / 2.0) / img_h
        norm_w = w / img_w
        norm_h = h / img_h

        return (x_center, y_center, norm_w, norm_h)

    def stop_robot(self):
        cmd = Twist()
        self.pub_cmd_vel.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    generator = SyntheticDatasetGenerator()
    rclpy.spin(generator)
    generator.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
