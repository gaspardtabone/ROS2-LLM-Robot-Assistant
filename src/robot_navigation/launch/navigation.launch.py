import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    pkg_nav = get_package_share_directory('robot_navigation')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    default_nav2_params = os.path.join(pkg_nav, 'config', 'nav2_params.yaml')
    default_map = os.path.join(pkg_nav, 'maps', 'appartement.yaml')

    params_arg = DeclareLaunchArgument(
        name='params_file',
        default_value=default_nav2_params,
        description='Full path to Nav2 params yaml'
    )

    map_arg = DeclareLaunchArgument(
        name='map',
        default_value=default_map,
        description='Full path to map yaml file'
    )

    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'map': LaunchConfiguration('map'),
            'params_file': LaunchConfiguration('params_file'),
            'use_sim_time': 'true',
            'autostart': 'true'
        }.items()
    )

    return LaunchDescription([
        params_arg,
        map_arg,
        nav2_bringup_launch
    ])
