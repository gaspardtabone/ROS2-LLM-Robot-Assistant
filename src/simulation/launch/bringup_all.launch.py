import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_sim = get_package_share_directory('simulation')
    pkg_nav = get_package_share_directory('robot_navigation')
    pkg_perc = get_package_share_directory('robot_perception')

    # 1. Simulation bringup
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_sim, 'launch', 'simulation.launch.py')
        )
    )

    # 2. Navigation bringup
    nav_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav, 'launch', 'navigation.launch.py')
        )
    )

    # 3. Perception bringup
    perc_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_perc, 'launch', 'perception.launch.py')
        )
    )

    # 4. Memory Node
    memory_node = Node(
        package='robot_memory',
        executable='memory_node',
        name='memory_node',
        output='screen'
    )

    # 5. LLM Bridge Node
    llm_node = Node(
        package='robot_llm',
        executable='llm_bridge_node',
        name='llm_bridge_node',
        output='screen'
    )

    # 6. Task Planner Node
    planner_node = Node(
        package='robot_planner',
        executable='task_planner_node',
        name='task_planner_node',
        output='screen'
    )

    return LaunchDescription([
        sim_launch,
        nav_launch,
        perc_launch,
        memory_node,
        llm_node,
        planner_node
    ])
