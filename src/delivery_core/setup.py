import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'delivery_core'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        
        # Tell ROS 2 to copy the launch files into the install directory
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        
        # Tell ROS 2 to copy the URDF files (from Phase 1)
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
        
        # Tell ROS 2 to copy the custom Worlds files
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.world')),
        
        # Tell ROS 2 to copy the QR Code Textures and Scripts (Phase 2)
        (os.path.join('share', package_name, 'materials', 'scripts'), glob('materials/scripts/*.material')),
        (os.path.join('share', package_name, 'materials', 'textures'), glob('materials/textures/*.png')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Gouransh Bhatnagar',
    maintainer_email='gouranshb2002@gmail.com',
    description='Collaborative AI Delivery System',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'detector_node = delivery_core.detector_node:main',
            'patrol_node = delivery_core.patrol_node:main',
            'central_planner = delivery_core.central_planner:main',
        ],
    },
)