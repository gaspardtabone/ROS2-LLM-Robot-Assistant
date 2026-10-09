import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray, Detection2D, ObjectHypothesisWithPose
import cv2
from cv_bridge import CvBridge
import numpy as np

try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False


class YoloDetectorNode(Node):
    def __init__(self):
        super().__init__('yolo_detector_node')

        self.declare_parameter('model_path', 'yolo11n.pt')
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('image_topic', '/camera/image_raw')

        self.model_path = self.get_parameter('model_path').get_parameter_value().string_value
        self.conf_thresh = self.get_parameter('confidence_threshold').get_parameter_value().double_value
        self.image_topic = self.get_parameter('image_topic').get_parameter_value().string_value

        self.bridge = CvBridge()
        self.model = None

        if ULTRALYTICS_AVAILABLE:
            try:
                self.model = YOLO(self.model_path)
                self.get_logger().info(f"Loaded YOLO model from '{self.model_path}'")
            except Exception as e:
                self.get_logger().warn(f"Failed to load YOLO model: {e}. Running in mock mode.")
        else:
            self.get_logger().warn("Ultralytics package not found. Running detector node in mock mode.")

        # Subscriptions and Publishers (Mike Likes Robots pattern)
        self.sub_image = self.create_subscription(
            Image,
            self.image_topic,
            self.image_callback,
            10
        )

        self.pub_detections = self.create_publisher(
            Detection2DArray,
            '/detected_objects',
            10
        )

        self.pub_annotated = self.create_publisher(
            Image,
            '/perception/image_annotated',
            10
        )

    def image_callback(self, msg: Image):
        try:
            cv_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f"CvBridge conversion error: {e}")
            return

        detection_array = Detection2DArray()
        detection_array.header = msg.header
        annotated_img = cv_img.copy()

        if self.model is not None:
            results = self.model.predict(cv_img, conf=self.conf_thresh, verbose=False)

            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    label = self.model.names[cls_id]
                    conf = float(box.conf[0])
                    xyxy = box.xyxy[0].cpu().numpy()

                    # Create Vision Msg Detection
                    detection = Detection2D()
                    detection.header = msg.header
                    
                    x_center = float((xyxy[0] + xyxy[2]) / 2.0)
                    y_center = float((xyxy[1] + xyxy[3]) / 2.0)
                    width = float(xyxy[2] - xyxy[0])
                    height = float(xyxy[3] - xyxy[1])

                    detection.bbox.center.position.x = x_center
                    detection.bbox.center.position.y = y_center
                    detection.bbox.size_x = width
                    detection.bbox.size_y = height

                    hypothesis = ObjectHypothesisWithPose()
                    hypothesis.hypothesis.class_id = label
                    hypothesis.hypothesis.score = conf
                    detection.results.append(hypothesis)

                    detection_array.detections.append(detection)

                    # Annotate image
                    cv2.rectangle(
                        annotated_img,
                        (int(xyxy[0]), int(xyxy[1])),
                        (int(xyxy[2]), int(xyxy[3])),
                        (0, 255, 0),
                        2
                    )
                    cv2.putText(
                        annotated_img,
                        f"{label} {conf:.2f}",
                        (int(xyxy[0]), max(int(xyxy[1]) - 10, 0)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2
                    )

        # Publish results
        self.pub_detections.publish(detection_array)

        try:
            annotated_msg = self.bridge.cv2_to_imgmsg(annotated_img, encoding='bgr8')
            annotated_msg.header = msg.header
            self.pub_annotated.publish(annotated_msg)
        except Exception as e:
            self.get_logger().error(f"Error publishing annotated image: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = YoloDetectorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
