# ROS 2 Jazzy Pan-Tilt Mechanism Simulation

This package simulates a two-degree-of-freedom pan-tilt gimbal mechanism using ROS 2 Jazzy, URDF, and RViz 2, with both manual user control and autonomous modes.

---

## Quick Start (Easiest Way)

Simply open a terminal in this workspace and run:

```bash
./run_sim.sh
```

This will automatically source ROS 2, source the workspace, and launch both **RViz 2** and the **Interactive Control Panel**.

---

## Standard Terminal Commands

If you prefer to run it manually step-by-step:

### 1. Open a terminal and source the setup files:
```bash
source /opt/ros/jazzy/setup.bash
source ~/pan_tilt_sim_ws/install/setup.bash
```

### 2. Launch the simulation:
```bash
ros2 launch pan_tilt_video_sim simulation.launch.py
```

---

## Operating Modes

When launched, the simulation starts in **Manual Mode** (stationary at `0, 0`), so you can move it yourself using the GUI sliders or arrow keys.

You can switch modes via the buttons in the GUI or from a second terminal:

- **Manual Control (You move it)**:
  ```bash
  ros2 topic pub --once /gimbal/mode std_msgs/msg/String "{data: 'manual'}"
  # Command specific angles (in radians):
  ros2 topic pub --once /gimbal/manual_command sensor_msgs/msg/JointState "{name: ['pan_joint', 'tilt_joint'], position: [0.8, -0.4]}"
  ```

- **Auto Demo Mode (Continuous sinusoidal animation)**:
  ```bash
  ros2 topic pub --once /gimbal/mode std_msgs/msg/String "{data: 'demo'}"
  ```

- **Track Mode (Follows target point)**:
  ```bash
  ros2 topic pub --once /gimbal/mode std_msgs/msg/String "{data: 'track'}"
  ```

- **Home Mode (Smooth reset to 0,0)**:
  ```bash
  ros2 topic pub --once /gimbal/mode std_msgs/msg/String "{data: 'home'}"
  ```

- **Stop / Freeze (Lock current position)**:
  ```bash
  ros2 topic pub --once /gimbal/mode std_msgs/msg/String "{data: 'stop'}"
  ```

---

## If You Ever Modify the Code (Rebuild)

If you modify any files in the `src/` directory, rebuild with:

```bash
cd ~/pan_tilt_sim_ws
colcon build --symlink-install
source install/setup.bash
```

