from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([

        Node(
            package='conveyor_dashboard',
            executable='l510_node',
            name='l510_node',
            output='screen',
            parameters=[
                {'port': '/dev/ttyUSB0'},
                {'initial_speed': 10.0}
            ]
        ),

        Node(
            package='conveyor_dashboard',
            executable='webcam_node',
            name='webcam_node',
            output='screen'
        ),

        Node(
            package='conveyor_dashboard',
            executable='dashboard_node',
            name='dashboard_node',
            output='screen'
        ),
    ])