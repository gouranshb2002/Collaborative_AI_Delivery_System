# Use official ROS 2 Humble desktop image as the base
FROM osrf/ros:humble-desktop

# Set environment variables to prevent interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Set the Cyclone DDS as the default middleware
ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# Update system and install ROS 2 / System dependencies (Gazebo & Arm Controllers included)
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    ros-humble-navigation2 \
    ros-humble-nav2-bringup \
    ros-humble-turtlebot3* \
    ros-humble-rmw-cyclonedds-cpp \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-ros2-control \
    ros-humble-ros2-controllers \
    ros-humble-gazebo-ros2-control \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for AI Vision (YOLOv8 & OpenCV)
RUN pip3 install --no-cache-dir \
    ultralytics \
    opencv-python \
    setuptools==58.2.0 \
    "numpy<2"

# Create the ROS 2 workspace directory
RUN mkdir -p /root/collab_delivery_ws/src

# Set the working directory
WORKDIR /root/collab_delivery_ws

# Dynamically append paths and source the environment so defaults are never overwritten
RUN echo 'export TURTLEBOT3_MODEL=waffle' >> /root/.bashrc
RUN echo 'export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/opt/ros/humble/share/turtlebot3_gazebo/models' >> /root/.bashrc
RUN echo 'source /opt/ros/humble/setup.bash' >> /root/.bashrc
RUN echo 'if [ -f /root/collab_delivery_ws/install/setup.bash ]; then source /root/collab_delivery_ws/install/setup.bash; fi' >> /root/.bashrc

# FORCE THE VARIABLES: Inject directly into Docker's environment engine
ENV TURTLEBOT3_MODEL=waffle
ENV GAZEBO_MODEL_PATH=/usr/share/gazebo-11/models:/opt/ros/humble/share/turtlebot3_gazebo/models

# The container will open in bash by default
CMD ["bash"]
