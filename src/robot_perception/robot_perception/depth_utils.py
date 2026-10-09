import math
from geometry_msgs.msg import Pose

def estimate_3d_pose(x_pixel: float, y_pixel: float, img_width: int = 640, img_height: int = 480) -> Pose:
    """
    Estimates a 3D pose in robot coordinate system from 2D pixel coordinates
    assuming pinhole camera geometry on horizontal floor.
    """
    pose = Pose()
    fov_h = 1.089  # Radians
    f_x = (img_width / 2.0) / math.tan(fov_h / 2.0)

    # Normalized center offset
    dx = (x_pixel - (img_width / 2.0)) / f_x

    # Estimated distance assumption (or ray intersection with floor)
    estimated_distance = 1.5  # meters

    pose.position.x = estimated_distance
    pose.position.y = -dx * estimated_distance
    pose.position.z = 0.5
    pose.orientation.w = 1.0

    return pose
