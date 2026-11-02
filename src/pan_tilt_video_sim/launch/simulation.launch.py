from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg = get_package_share_directory('pan_tilt_video_sim')
    urdf = os.path.join(pkg, 'urdf', 'pan_tilt_video.urdf')
    rviz = os.path.join(pkg, 'config', 'display.rviz')

    return LaunchDescription([
        DeclareLaunchArgument(
            'mode',
            default_value='manual',
            description='Operating mode: manual, demo, track, stop, home'
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': open(urdf).read()}],
            output='screen'
        ),
        Node(
            package='pan_tilt_video_sim',
            executable='simulator',
            parameters=[{'mode': LaunchConfiguration('mode')}],
            output='screen'
        ),
        Node(
            package='pan_tilt_video_sim',
            executable='target_generator',
            output='screen'
        ),
        Node(
            package='pan_tilt_video_sim',
            executable='controller',
            output='screen'
        ),
        Node(
            package='pan_tilt_video_sim',
            executable='gui_control',
            output='screen'
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz],
            output='screen'
        )
    ])
