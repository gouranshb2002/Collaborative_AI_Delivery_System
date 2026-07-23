# Collaborative AI Delivery System
A fully autonomous, multi-robot logistics system built in ROS 2 (Humble). This project features AI-driven YOLO object detection, decentralized state-machine orchestration, and precise 5-DOF robotic arm kinematics to seamlessly bridge the gap between Gazebo simulation and physical hardware deployment.

## Project Versions & Branches
This repository is maintained across two official versions depending on your execution preference:

*   **`v1.1-with-docker` (Recommended):** Pre-packaged with a complete Docker environment. It isolates ROS 2 Humble, Gazebo, and OpenCV dependencies inside a container to guarantee a 100% bug-free setup across all systems.
*   **`v1.0-no-docker`:** Pure ROS 2 workspace containing only the source code. Use this branch if you prefer a native, non-containerized installation on a local Ubuntu 22.04 machine.
You can switch between these versions using the branch dropdown menu at the top-left of the GitHub repository page.

## Summary
This project presents a fully autonomous, multi-robot delivery architecture designed to solve decentralized logistics challenges. The system orchestrates two distinct TurtleBot3 platforms to execute complex supply-chain tasks without human intervention:
1. **The Detector Bot (Vision & Mapping):** Navigates the facility to locate inventory using an onboard camera and YOLO-based AI object detection.
2. **The Central Planner (Master Node):** A centralized intelligence that manages a randomized order queue, processes the map data, and dispatches collision-free navigation commands.
3. **The Delivery Bot (Retrieval & Delivery):** Uses an OpenManipulator-X robotic arm to execute precise Joint Trajectory kinematics to pick up items and transport them to a designated drop-off zone.

## Technology Stack
- **Framework:** ROS 2 (Humble) / Ubuntu 22.04 LTS
- **Simulation:** Gazebo 11
- **Languages:** Python 3, XML (URDF/Launch)
- **Computer Vision & AI:** YOLO (Ultralytics), OpenCV, cv_bridge
- **Control Systems:** geometry_msgs/Twist, Quaternion Math, trajectory_msgs/JointTrajectory

## Installation
This project is built for Ubuntu 22.04 and ROS 2 Humble.
1. **This project is built for Ubuntu 22.04 and ROS 2 Humble.**

Open a terminal and install the required simulators, mapping tools, arm controllers, and AI vision libraries:

    sudo apt update
    sudo apt install ros-humble-gazebo-* ros-humble-cartographer ros-humble-cartographer-ros ros-humble-nav2-map-server ros-humble-urdf
    sudo apt install ros-humble-turtlebot3 ros-humble-turtlebot3-msgs ros-humble-turtlebot3-simulations
    sudo apt install ros-humble-dynamixel-sdk ros-humble-dynamixel-workbench-toolbox
    sudo apt install ros-humble-turtlebot3-manipulation ros-humble-turtlebot3-manipulation-hardware
    sudo apt install python3-opencv ros-humble-cv-bridge ros-humble-vision-opencv
    pip3 install ultralytics

2. **Set Default Robot Model**

Add the TurtleBot3 Waffle model to your bash profile:

    echo 'export TURTLEBOT3_MODEL=waffle' >> ~/.bashrc
    source ~/.bashrc

3. **Build the Workspace**

Clone this repository into a ROS 2 workspace and build it:

    mkdir -p ~/collab_delivery_ws/src
    cd ~/collab_delivery_ws/src

Clone the repository here:

    git clone https://github.com/gouranshb2002/Collaborative_AI_Delivery_System.git .
    cd ~/collab_delivery_ws
    colcon build --symlink-install
    source install/setup.bash

## How to Run (Gazebo Simulation)
To run the complete autonomous orchestration in Gazebo, open 4 separate terminals and run the following commands in order.
Note: Make sure to source your workspace ``source install/setup.bash`` in every terminal

**Terminal 1: Launch the Physical World & Robots**

    ros2 launch delivery_core multi_bot.launch.py
    
**Terminal 2: Launch the YOLO AI Vision (Detector)**

    ros2 run delivery_core detector_node

**Terminal 3: Launch the Facility Mapper (Patrol Route)**

    ros2 run delivery_core patrol_node

**Terminal 4: Launch the Central Planner (The Logistics Brain)**

    ros2 run delivery_core central_planner
Note: The Central Planner will wait 50 seconds for the facility to be mapped before dispatching the Deliverer Bot to fulfill the order queue

## Physical Hardware Deployment Guide
When deploying to physical TurtleBot3 hardware, the Python logic remains identical, but the processing load must be distributed properly. YOLO requires heavy computing power, so the AI node should run on your Host PC, while the robots just stream data and drive.

### 1. Network Setup

Your Host PC and both TurtleBots must be connected to the exact same Wi-Fi network. Ensure they all share the same ROS Domain ID by adding this to the ``~/.bashrc`` of all machines:

    export ROS_DOMAIN_ID=30

### 2. Physical Bringup

Do not run Terminal 1 ``multi_bot.launch.py``. Instead, SSH into the physical robots and launch their hardware directly:
- Detector Bot: ``ros2 launch turtlebot3_bringup robot.launch.py``
- Delivery Bot: ``ros2 launch turtlebot3_manipulation_bringup hardware.launch.py``

### 3. Camera Streaming

Gazebo fakes a camera. On the physical Detector Bot, you must launch a ROS 2 camera node to stream images back to your laptop:

    ros2 run v4l2_camera v4l2_camera_node --ros-args -p image_size:="[640,480]"

### 4. Run AI and Logic

Because YOLO is heavy, run the logic nodes on your laptop. The laptop will receive the camera stream over Wi-Fi, run the YOLO neural network, and send movement commands back to the robots.
Run Terminals 2, 3, and 4 from your Host PC!

### 5. Real-World Coordinate Calibration

In simulation, the walls are mathematically perfect. In the real world, odometry drift occurs. Open ``central_planner.py`` and ``patrol_node.py``, and update the ``self.pickup_zones`` and ``self.delivery_station`` coordinates to match the measured geometry of your physical room to prevent the robots from hitting walls.

## Academic Information
- Author: Gouransh Bhatnagar
- University: Technische Hochschule Deggendorf (Campus Cham)
- LinkedIn: https://linkedin.com/in/gouranshbhatnagar
- License: Apache License 2.0
