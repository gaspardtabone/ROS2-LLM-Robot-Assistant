from setuptools import find_packages, setup

package_name = 'robot_memory'

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
    description='SQLite persistence node for domestic assistant',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'memory_node = robot_memory.memory_node:main',
        ],
    },
)
