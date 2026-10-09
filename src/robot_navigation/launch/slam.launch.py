import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_nav = get_package_share_directory('robot_navigation')
    default_params_file = os.path.join(pkg_nav, 'config', 'slam_toolbox_params.yaml')

    params_arg = DeclareLaunchArgument(
        name='params_file',
        default_value=default_params_file,
        description='Full path to the ROS2 parameters file to use for slam_toolbox'
    )

    slam_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[LaunchConfiguration('params_file'), {'use_sim_time': True}]
    )

    return LaunchDescription([
        params_arg,
        slam_node
    ])
