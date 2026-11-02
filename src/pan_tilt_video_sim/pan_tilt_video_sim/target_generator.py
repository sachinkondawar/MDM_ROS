import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PointStamped
class Target(Node):
 def __init__(self):
  super().__init__('target_generator');self.pub=self.create_publisher(PointStamped,'/gimbal/target_pixel',10);self.t=0.0;self.create_timer(0.05,self.tick)
 def tick(self):
  self.t+=0.05;m=PointStamped();m.header.stamp=self.get_clock().now().to_msg();m.header.frame_id='image_640x480';m.point.x=320+190*math.sin(self.t*0.65);m.point.y=240+125*math.sin(self.t*0.42+0.8);self.pub.publish(m)
def main():
 rclpy.init();n=Target();rclpy.spin(n);n.destroy_node();rclpy.shutdown()
