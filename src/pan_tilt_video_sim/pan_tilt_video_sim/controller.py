import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PointStamped
from sensor_msgs.msg import JointState
from std_msgs.msg import String
class Controller(Node):
 def __init__(self):
  super().__init__('tracking_controller');self.declare_parameter('kp_pan',0.75);self.declare_parameter('kp_tilt',0.65);self.declare_parameter('deadband_px',8.0);self.declare_parameter('max_rate',0.8);self.pan=0.;self.tilt=0.;self.last=None;self.enabled=True;self.create_subscription(PointStamped,'/gimbal/target_pixel',self.target,10);self.create_subscription(String,'/gimbal/mode',self.mode,10);self.pub=self.create_publisher(JointState,'/gimbal/servo_command',10);self.create_timer(0.02,self.tick)
 def mode(self,msg):self.enabled=msg.data.strip().lower()!='stop'
 def target(self,msg):self.last=(float(msg.point.x),float(msg.point.y),self.get_clock().now().nanoseconds/1e9)
 def tick(self):
  now=self.get_clock().now().nanoseconds/1e9;dt=0.02
  if self.enabled and self.last is not None and now-self.last[2]<0.5:
   x,y,_=self.last;ex=(x-320)/320;ey=(y-240)/240
   if abs(x-320)>self.get_parameter('deadband_px').value:self.pan-=max(-0.8,min(0.8,self.get_parameter('kp_pan').value*ex))*dt
   if abs(y-240)>self.get_parameter('deadband_px').value:self.tilt+=max(-0.8,min(0.8,self.get_parameter('kp_tilt').value*ey))*dt
  self.pan=max(-2.8,min(2.8,self.pan));self.tilt=max(-1.2,min(1.2,self.tilt))
  msg=JointState();msg.header.stamp=self.get_clock().now().to_msg();msg.name=['pan_joint','tilt_joint'];msg.position=[self.pan,self.tilt];self.pub.publish(msg)
def main():
 rclpy.init();n=Controller();rclpy.spin(n);n.destroy_node();rclpy.shutdown()
