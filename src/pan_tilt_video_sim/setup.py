from setuptools import setup
from glob import glob

package_name = 'pan_tilt_video_sim'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
        ('share/' + package_name + '/urdf', glob('urdf/*.urdf')),
        ('share/' + package_name + '/config', glob('config/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Sachin Kondawar',
    maintainer_email='kondawarsachin22@gmail.com',
    description='Video inspired pan tilt ROS 2 simulation with manual and autonomous control',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'simulator = pan_tilt_video_sim.simulator:main',
            'controller = pan_tilt_video_sim.controller:main',
            'target_generator = pan_tilt_video_sim.target_generator:main',
            'gui_control = pan_tilt_video_sim.gui_control:main',
        ],
    },
)
