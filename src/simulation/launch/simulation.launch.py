import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_sim = get_package_share_directory('simulation')
    pkg_desc = get_package_share_directory('robot_description')

    world_path = os.path.join(pkg_sim, 'worlds', 'appartement.sdf')
    xacro_path = os.path.join(pkg_desc, 'urdf', 'robot.urdf.xacro')
    bridge_config_path = os.path.join(pkg_sim, 'config', 'ros_gz_bridge.yaml')

    world_arg = DeclareLaunchArgument(
        name='world',
        default_value=world_path,
        description='Path to SDF world file'
    )

    # 1. Start Gazebo Fortress World
    gazebo_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': ['-r ', LaunchConfiguration('world')]}.items()
    )

    # 2. Robot State Publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'robot_description': Command(['xacro ', xacro_path])
        }]
    )

    # 3. Spawn Robot in Gazebo Fortress
    spawn_robot_node = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-name', 'domestic_assistant',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1',
            '-Y', '0.0'
        ]
    )

    # 4. ROS GZ Parameter Bridge
    ros_gz_bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        parameters=[{'config_file': bridge_config_path}]
    )

    return LaunchDescription([
        world_arg,
        gazebo_sim,
        robot_state_publisher_node,
        spawn_robot_node,
        ros_gz_bridge_node
    ])
