# ROS 2 Jazzy Pan-Tilt Video-Inspired Simulation

This package recreates the **visible general shape and two-axis motion** of the provided SolidWorks animation, using a parameterised URDF approximation (not the original CAD). It runs in RViz 2. This is a **kinematic** joint simulation, not Gazebo physics or a real camera simulation.

## Install (Ubuntu 24.04, ROS 2 Jazzy)

```bash
sudo apt update
sudo apt install ros-jazzy-desktop ros-jazzy-robot-state-publisher python3-colcon-common-extensions
mkdir -p ~/pan_tilt_ws/src
unzip pan_tilt_video_sim.zip -d ~/pan_tilt_ws/src
source /opt/ros/jazzy/setup.bash
cd ~/pan_tilt_ws
colcon build --symlink-install
source install/setup.bash
ros2 launch pan_tilt_video_sim simulation.launch.py
```

The ZIP contains a top-level `pan_tilt_video_sim/` ROS package. Launch starts the URDF model, joint simulator, synthetic target, controller, and RViz together.

## Options (second terminal; source ROS + workspace first)

```bash
source /opt/ros/jazzy/setup.bash
source ~/pan_tilt_ws/install/setup.bash
# Motion resembling the SolidWorks video (default)
ros2 topic pub --once /gimbal/mode std_msgs/msg/String "{data: demo}"
# Automatic simulated pixel target tracking
ros2 topic pub --once /gimbal/mode std_msgs/msg/String "{data: track}"
# Freeze the joints
ros2 topic pub --once /gimbal/mode std_msgs/msg/String "{data: stop}"
# Return joints to zero
ros2 topic pub --once /gimbal/mode std_msgs/msg/String "{data: home}"
```

To launch directly in tracking mode:

```bash
ros2 launch pan_tilt_video_sim simulation.launch.py mode:=track
```

To inspect values:

```bash
ros2 topic echo /joint_states
ros2 topic echo /gimbal/target_pixel
ros2 topic echo /gimbal/servo_command
```

## Logic

- Demo mode: sinusoidal pan and tilt references, limited by joint speed.
- Track mode: synthetic target publishes pixel coordinates for a 640x480 image. Controller applies proportional angular velocity to reduce the centre error. Joint simulator applies rate-limited commands and publishes `/joint_states` for `robot_state_publisher` and RViz.
- Home mode: smoothly returns pan and tilt to zero.
- Stop mode: holds current joint positions.
- Pan mechanical limits: ±2.8 rad; tilt: ±1.2 rad. Default joint speed 1 rad/s.

## Notes

- The SolidWorks video does not provide dimensions or motion timing, so this is an approximate model and animation.
- RViz is a 3D visualiser, not a physics simulator. No camera imagery, detection, servo electronics, collision response or motor torque are modelled.
- The proportional controller sign conventions assume an image view with the camera facing -Y. For real cameras, calibrate signs, optics, and angular rates.
- In the current starter, the synthetic target does not respond to camera motion. Therefore tracking mode demonstrates a control pipeline but **is not a physically closed-loop camera tracking simulation**.
- For a genuinely closed-loop scene use Gazebo + camera sensor + image processing + actuator plugins.
