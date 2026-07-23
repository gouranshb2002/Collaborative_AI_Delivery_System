# Collaborative AI Delivery System (v1.1)
A fully autonomous, multi-robot logistics system built in ROS 2 (Humble). This project features AI-driven YOLO object detection, decentralized state-machine orchestration, and precise 5-DOF robotic arm kinematics to seamlessly bridge the gap between Gazebo simulation and physical hardware deployment.

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

## Step-by-Step Execution Guide
This project runs inside a fully pre-configured Docker container. To launch the complete simulation, open 4 separate terminal tabs on your host machine and follow these steps in order.

**Step 1: Build the Docker Environment (First Time Only)**

Open a terminal in your project directory and build the container image:

    ./build_docker.sh
**Terminal 1: The World (Gazebo & Robots)**

Open your main terminal, start the container, build the workspace, and launch the multi-robot world:

    ./run_docker.sh
Once inside the container shell, run:

    cd ~/collab_delivery_ws
    colcon build --symlink-install
    source /opt/ros/humble/setup.bash
    source install/setup.bash
    ros2 launch delivery_core multi_bot.launch.py
Note: Wait until the Gazebo GUI opens and both Waffle bots are fully spawned before proceeding.

**Terminal 2: The Vision (YOLOv8 & QR Detector)**
1. Open a new terminal tab on your host machine.
2. Attach into the running container:

       ./into_docker.sh
3. Source the environment and start the vision node:
   
        cd ~/collab_delivery_ws
        source /opt/ros/humble/setup.bash
        source install/setup.bash
        ros2 run delivery_core detector_node

**Terminal 3: The Mapper (Patrol Route)**
1. Open a third terminal tab on your host machine.
2. Attach into the running container:

        ./into_docker.sh
3. Source the environment and start the patrol node:

        cd ~/collab_delivery_ws
        source /opt/ros/humble/setup.bash
        source install/setup.bash
        ros2 run delivery_core patrol_node

**Terminal 4: The Central Planner (Logistics Brain)**
1. Open your fourth terminal tab on your host machine.
2. Attach into the running container:

        ./into_docker.sh
3. Source the environment and start the central orchestrator:

        cd ~/collab_delivery_ws
        source /opt/ros/humble/setup.bash
        source install/setup.bash
        ros2 run delivery_core central_planner
Note: The Central Planner will wait 50 seconds for the facility to be mapped before dispatching the Deliverer Bot to fulfill the order queue.

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
