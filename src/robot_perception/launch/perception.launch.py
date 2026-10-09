import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_perc = get_package_share_directory('robot_perception')
    params_path = os.path.join(pkg_perc, 'config', 'yolo_params.yaml')

    detector_node = Node(
        package='robot_perception',
        executable='detector_node',
        name='yolo_detector_node',
        output='screen',
        parameters=[params_path]
    )

    search_server_node = Node(
        package='robot_perception',
        executable='search_object_server',
        name='search_object_action_server',
        output='screen'
    )

    return LaunchDescription([
        detector_node,
        search_server_node
    ])
