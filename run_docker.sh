#!/bin/bash
# Runs the container with GUI support, auto-removes on exit, and mounts local workspace

# Allow local X11 connections for Gazebo and RViz
xhost +local:root

echo "Starting ROS 2 Collaborative AI Delivery System Container..."

docker run -it --rm \
    --net=host \
    --env="DISPLAY" \
    --env="QT_X11_NO_MITSHM=1" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
    --volume="$(pwd):/root/collab_delivery_ws/src/Collaborative_AI_Delivery_System" \
    --name collab_ai_container \
    collab_ai_delivery_img \
    bash
