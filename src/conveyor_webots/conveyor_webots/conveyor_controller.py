#!/usr/bin/env python3

from controller import Supervisor
import math

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class ConveyorRosNode(Node):
    def __init__(self):
        super().__init__('webots_conveyor_controller')
        self.speed = 0.0

        self.create_subscription(
            Float32,
            '/conveyor_speed',
            self.speed_callback,
            10
        )

    def speed_callback(self, msg):
        self.speed = float(msg.data)
        self.get_logger().info(f'Velocidad recibida: {self.speed:.3f} m/s')


robot = Supervisor()
timestep = int(robot.getBasicTimeStep())

rclpy.init()
ros_node = ConveyorRosNode()

roller_start = robot.getFromDef('RODILLO_INICIO')
roller_end = robot.getFromDef('RODILLO_FINAL')
box = robot.getFromDef('CAJA')

marks = [
    robot.getFromDef('MARCA_1'),
    robot.getFromDef('MARCA_2'),
    robot.getFromDef('MARCA_3'),
    robot.getFromDef('MARCA_4'),
]

roller_angle = 0.0
roller_radius = 0.05

x_min = -0.65
x_max = 0.65

while robot.step(timestep) != -1:
    dt = timestep / 1000.0

    rclpy.spin_once(ros_node, timeout_sec=0.0)

    speed = ros_node.speed

    omega = speed / roller_radius
    roller_angle += omega * dt
    roller_angle = roller_angle % (2.0 * math.pi)

    roller_start.getField('rotation').setSFRotation([0, 1, 0, roller_angle])
    roller_end.getField('rotation').setSFRotation([0, 1, 0, roller_angle])

    for mark in marks:
        field = mark.getField('translation')
        pos = field.getSFVec3f()
        pos[0] += speed * dt

        if pos[0] > x_max:
            pos[0] = x_min
        elif pos[0] < x_min:
            pos[0] = x_max

        field.setSFVec3f(pos)

    box_field = box.getField('translation')
    box_pos = box_field.getSFVec3f()
    box_pos[0] += speed * dt

    if box_pos[0] > x_max:
        box_pos[0] = x_min
    elif box_pos[0] < x_min:
        box_pos[0] = x_max

    box_field.setSFVec3f(box_pos)

ros_node.destroy_node()
rclpy.shutdown()
