#!/usr/bin/env bash
# Phase 0 — ROS 2 Humble environment setup (Ubuntu 22.04)
set -euo pipefail

if [[ "${ROS_DISTRO:-}" != "humble" ]]; then
  echo "Source ROS 2 Humble first: source /opt/ros/humble/setup.bash"
  exit 1
fi

sudo apt update
sudo apt install -y \
  ros-humble-desktop \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-slam-toolbox \
  ros-humble-robot-state-publisher \
  ros-humble-xacro \
  ros-humble-joint-state-publisher-gui \
  ros-humble-ros-gz \
  ros-humble-ros-gz-sim \
  ros-humble-ros-gz-bridge \
  ros-humble-cv-bridge \
  ros-humble-image-transport \
  ros-humble-vision-msgs \
  ros-humble-teleop-twist-keyboard \
  python3-colcon-common-extensions \
  python3-pip

pip3 install --user ultralytics opencv-python pydantic anthropic

echo "Setup complete. Build with:"
echo "  cd $(dirname "$0")/.. && colcon build && source install/setup.bash"
