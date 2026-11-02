import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String

class Simulator(Node):
    def __init__(self):
        super().__init__('joint_simulator')
        self.declare_parameter('mode', 'manual')
        self.declare_parameter('max_joint_speed', 1.5)
        self.mode = str(self.get_parameter('mode').value).strip().lower()
        self.pan = 0.0
        self.tilt = 0.0
        self.goal_pan = 0.0
        self.goal_tilt = 0.0
        self.t = 0.0
        self.create_subscription(JointState, '/gimbal/servo_command', self.command, 10)
        self.create_subscription(JointState, '/gimbal/manual_command', self.manual_command, 10)
        self.create_subscription(String, '/gimbal/mode', self.set_mode, 10)
        self.pub = self.create_publisher(JointState, '/joint_states', 10)
        self.create_timer(0.02, self.tick)
        self.get_logger().info(f'Joint Simulator initialized in mode: {self.mode}')

    def manual_command(self, m):
        if self.mode == 'manual':
            for name, pos in zip(m.name, m.position):
                if name == 'pan_joint':
                    self.goal_pan = max(-2.8, min(2.8, float(pos)))
                if name == 'tilt_joint':
                    self.goal_tilt = max(-1.2, min(1.2, float(pos)))

    def command(self, m):
        if self.mode == 'track':
            for name, pos in zip(m.name, m.position):
                if name == 'pan_joint':
                    self.goal_pan = max(-2.8, min(2.8, float(pos)))
                if name == 'tilt_joint':
                    self.goal_tilt = max(-1.2, min(1.2, float(pos)))

    def set_mode(self, m):
        new_mode = m.data.strip().lower()
        if new_mode in ('demo', 'track', 'stop', 'home', 'manual'):
            self.mode = new_mode
            if self.mode == 'home':
                self.goal_pan = 0.0
                self.goal_tilt = 0.0
            self.get_logger().info('Mode changed to: ' + self.mode)

    def tick(self):
        self.t += 0.02
        if self.mode == 'demo':
            a = 0.95 * math.sin(self.t * 0.52)
            b = 0.55 * math.sin(self.t * 0.76)
        elif self.mode == 'home':
            a = 0.0
            b = 0.0
        elif self.mode in ('track', 'manual'):
            a = self.goal_pan
            b = self.goal_tilt
        else:
            a = self.pan
            b = self.tilt

        max_step = float(self.get_parameter('max_joint_speed').value) * 0.02
        self.pan += max(-max_step, min(max_step, a - self.pan))
        self.tilt += max(-max_step, min(max_step, b - self.tilt))

        m = JointState()
        m.header.stamp = self.get_clock().now().to_msg()
        m.name = ['pan_joint', 'tilt_joint']
        m.position = [self.pan, self.tilt]
        self.pub.publish(m)

def main():
    rclpy.init()
    n = Simulator()
    try:
        rclpy.spin(n)
    except KeyboardInterrupt:
        pass
    finally:
        n.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
