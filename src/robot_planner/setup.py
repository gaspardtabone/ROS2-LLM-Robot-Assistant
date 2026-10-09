from setuptools import find_packages, setup

package_name = 'robot_planner'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Gaspard',
    maintainer_email='user@todo.todo',
    description='FSM task planner node executing high-level robot missions.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'task_planner_node = robot_planner.task_planner_node:main',
        ],
    },
)
