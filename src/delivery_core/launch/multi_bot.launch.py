import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Package Paths
    pkg_delivery_core = get_package_share_directory('delivery_core')
    gazebo_ros_pkg = get_package_share_directory('gazebo_ros')
    tb3_gazebo_pkg = get_package_share_directory('turtlebot3_gazebo')
    tb3_desc_pkg = get_package_share_directory('turtlebot3_description')
    manipulation_gazebo_pkg = get_package_share_directory('turtlebot3_manipulation_gazebo')
    
    # CUSTOM WORLD & ROBOTS
    workspace_share_dir = os.path.dirname(pkg_delivery_core)
    gazebo_model_paths = os.environ.get('GAZEBO_MODEL_PATH', '').split(':')
    ament_prefix_paths = os.environ.get('AMENT_PREFIX_PATH', '').split(':')
    
    for ament_path in ament_prefix_paths:
        share_path = os.path.join(ament_path, 'share')
        if share_path not in gazebo_model_paths:
            gazebo_model_paths.append(share_path)
            
    tb3_models_dir = os.path.join(tb3_gazebo_pkg, 'models')
    if tb3_models_dir not in gazebo_model_paths:
        gazebo_model_paths.append(tb3_models_dir)
        
    os.environ['GAZEBO_MODEL_PATH'] = ':'.join([p for p in gazebo_model_paths if p])

    # 2. File Paths
    custom_world_path = os.path.join(pkg_delivery_core, 'worlds', 'delivery_apartment.world')
    waffle_urdf_path = os.path.join(tb3_desc_pkg, 'urdf', 'turtlebot3_waffle.urdf')
    waffle_sdf_path = os.path.join(tb3_gazebo_pkg, 'models', 'turtlebot3_waffle', 'model.sdf')
    
    with open(waffle_urdf_path, 'r') as infp:
        waffle_urdf_content = infp.read()

    return LaunchDescription([

        # 1. LAUNCH GAZEBO, APARTMENT, & DELIVERER WAFFLE
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(manipulation_gazebo_pkg, 'launch', 'gazebo.launch.py')
            ),
            launch_arguments={
                'world': custom_world_path, # Pass our custom world instead of empty.world
                'x_pose': '-0.5',  
                'y_pose': '-0.2',
                'z_pose': '0.05'
            }.items()
        ),

        # 2. DETECTOR WAFFLE NODES
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='detector_state_publisher',
            namespace='detector_bot',
            parameters=[{
                'robot_description': waffle_urdf_content,
                'use_sim_time': True,
                'frame_prefix': 'detector_bot/'
            }],
            output='screen'
        ),
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-entity', 'detector_waffle',
                '-file', waffle_sdf_path,
                '-robot_namespace', 'detector_bot',
                '-x', '-0.5',   
                '-y', '-0.7',
                '-z', '0.05'
            ],
            output='screen'
        )
    ])