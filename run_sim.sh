#!/usr/bin/env bash
# ==============================================================================
# Script to launch the Pan-Tilt Video Simulation and Interactive GUI Controller
# ==============================================================================

# Source ROS 2 Jazzy
if [ -f "/opt/ros/jazzy/setup.bash" ]; then
    source /opt/ros/jazzy/setup.bash
else
    echo "Error: /opt/ros/jazzy/setup.bash not found. Ensure ROS 2 Jazzy is installed."
    exit 1
fi

# Source workspace install directory
WS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$WS_DIR/install/setup.bash" ]; then
    source "$WS_DIR/install/setup.bash"
else
    echo "Warning: $WS_DIR/install/setup.bash not found. Building workspace first..."
    cd "$WS_DIR" && colcon build --symlink-install
    source "$WS_DIR/install/setup.bash"
fi

# Launch simulation
echo "Starting Pan-Tilt Simulation and Control Panel..."
ros2 launch pan_tilt_video_sim simulation.launch.py "$@"

