import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'robot_perception'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=true,
    maintainer='Gaspard',
    maintainer_email='user@todo.todo',
    description='Perception node and search action server using YOLO and ROS 2.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'detector_node = robot_perception.detector_node:main',
            'search_object_server = robot_perception.search_object_server:main',
            'dataset_generator = robot_perception.dataset_generator:main',
        ],
    },
)
