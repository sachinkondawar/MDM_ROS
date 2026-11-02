import math
import threading
import tkinter as tk
from tkinter import ttk
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import PointStamped
from std_msgs.msg import String

class PanTiltGuiNode(Node):
    def __init__(self):
        super().__init__('pan_tilt_gui_controller')
        self.pub_mode = self.create_publisher(String, '/gimbal/mode', 10)
        self.pub_manual = self.create_publisher(JointState, '/gimbal/manual_command', 10)
        self.pub_target = self.create_publisher(PointStamped, '/gimbal/target_pixel', 10)
        
        self.actual_pan = 0.0
        self.actual_tilt = 0.0
        self.current_mode = 'manual'
        
        self.create_subscription(JointState, '/joint_states', self.cb_joint_states, 10)
        self.create_subscription(String, '/gimbal/mode', self.cb_mode, 10)

    def cb_joint_states(self, msg):
        for name, pos in zip(msg.name, msg.position):
            if name == 'pan_joint':
                self.actual_pan = pos
            elif name == 'tilt_joint':
                self.actual_tilt = pos

    def cb_mode(self, msg):
        self.current_mode = msg.data.strip().lower()

    def set_mode(self, mode_name):
        self.current_mode = mode_name.lower()
        msg = String()
        msg.data = self.current_mode
        self.pub_mode.publish(msg)

    def send_manual_joint(self, pan_rad, tilt_rad):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['pan_joint', 'tilt_joint']
        msg.position = [float(pan_rad), float(tilt_rad)]
        self.pub_manual.publish(msg)

    def send_target_pixel(self, x, y):
        msg = PointStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'image_640x480'
        msg.point.x = float(x)
        msg.point.y = float(y)
        self.pub_target.publish(msg)

class PanTiltApp:
    def __init__(self, root, node):
        self.root = root
        self.node = node
        self.root.title("Pan-Tilt Manual & Interactive Control")
        self.root.geometry("520x680")
        self.root.resizable(False, False)

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.cmd_pan_deg = tk.DoubleVar(value=0.0)
        self.cmd_tilt_deg = tk.DoubleVar(value=0.0)
        self.mode_var = tk.StringVar(value="MANUAL")
        self.actual_readout_var = tk.StringVar(value="Actual: Pan: 0.0° | Tilt: 0.0°")

        self._build_ui()
        self._bind_keys()
        self._start_periodic_update()

        # Send initial manual mode
        self.set_mode('manual')

    def _build_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#1e222d", pady=12)
        header_frame.pack(fill=tk.X)
        title_lbl = tk.Label(header_frame, text="Pan-Tilt Mechanism Controller", font=("DejaVu Sans", 14, "bold"), fg="#ffffff", bg="#1e222d")
        title_lbl.pack()
        sub_lbl = tk.Label(header_frame, text="Interactive Manual & Autonomous Modes", font=("DejaVu Sans", 9), fg="#9ba1b0", bg="#1e222d")
        sub_lbl.pack()

        # Mode Selection Section
        mode_box = tk.LabelFrame(self.root, text=" 🎮 Operating Mode ", font=("DejaVu Sans", 10, "bold"), padx=10, pady=8)
        mode_box.pack(fill=tk.X, padx=14, pady=8)

        status_row = tk.Frame(mode_box)
        status_row.pack(fill=tk.X, pady=(0, 6))
        tk.Label(status_row, text="Active Mode:", font=("DejaVu Sans", 10, "bold")).pack(side=tk.LEFT)
        self.status_lbl = tk.Label(status_row, textvariable=self.mode_var, font=("DejaVu Sans", 10, "bold"), fg="#2e7d32", bg="#e8f5e9", padx=8, pady=2, relief=tk.SOLID, bd=1)
        self.status_lbl.pack(side=tk.LEFT, padx=8)

        btn_grid = tk.Frame(mode_box)
        btn_grid.pack(fill=tk.X, pady=4)
        
        btn_manual = tk.Button(btn_grid, text="🖐️ Manual (You Move)", font=("DejaVu Sans", 9, "bold"), bg="#1976d2", fg="white", activebackground="#1565c0", relief=tk.RAISED, padx=6, pady=4, command=lambda: self.set_mode('manual'))
        btn_manual.grid(row=0, column=0, padx=3, pady=3, sticky="nsew")

        btn_demo = tk.Button(btn_grid, text="▶️ Auto Demo", font=("DejaVu Sans", 9), bg="#455a64", fg="white", activebackground="#37474f", relief=tk.RAISED, padx=6, pady=4, command=lambda: self.set_mode('demo'))
        btn_demo.grid(row=0, column=1, padx=3, pady=3, sticky="nsew")

        btn_track = tk.Button(btn_grid, text="🎯 Track Target", font=("DejaVu Sans", 9), bg="#455a64", fg="white", activebackground="#37474f", relief=tk.RAISED, padx=6, pady=4, command=lambda: self.set_mode('track'))
        btn_track.grid(row=0, column=2, padx=3, pady=3, sticky="nsew")

        btn_home = tk.Button(btn_grid, text="🏠 Home (0,0)", font=("DejaVu Sans", 9), bg="#388e3c", fg="white", activebackground="#2e7d32", relief=tk.RAISED, padx=6, pady=4, command=self.go_home)
        btn_home.grid(row=1, column=0, padx=3, pady=3, sticky="nsew")

        btn_stop = tk.Button(btn_grid, text="⏹️ Stop / Freeze", font=("DejaVu Sans", 9, "bold"), bg="#d32f2f", fg="white", activebackground="#b71c1c", relief=tk.RAISED, padx=6, pady=4, command=lambda: self.set_mode('stop'))
        btn_stop.grid(row=1, column=1, columnspan=2, padx=3, pady=3, sticky="nsew")

        for c in range(3):
            btn_grid.grid_columnconfigure(c, weight=1)

        # Manual Sliders Section
        slider_box = tk.LabelFrame(self.root, text=" 🕹️ Manual Joint Control (Sliders & Arrow Keys) ", font=("DejaVu Sans", 10, "bold"), padx=12, pady=10)
        slider_box.pack(fill=tk.X, padx=14, pady=6)

        # Pan Slider
        pan_header = tk.Frame(slider_box)
        pan_header.pack(fill=tk.X)
        tk.Label(pan_header, text="Pan Joint (Horizontal):", font=("DejaVu Sans", 9, "bold")).pack(side=tk.LEFT)
        self.pan_val_lbl = tk.Label(pan_header, text="0.0° (0.00 rad)", font=("DejaVu Sans", 9), fg="#1565c0")
        self.pan_val_lbl.pack(side=tk.RIGHT)

        self.pan_scale = tk.Scale(slider_box, from_=-160.0, to=160.0, resolution=1.0, orient=tk.HORIZONTAL, variable=self.cmd_pan_deg, showvalue=False, command=self.on_slider_change)
        self.pan_scale.pack(fill=tk.X, pady=(2, 8))

        # Tilt Slider
        tilt_header = tk.Frame(slider_box)
        tilt_header.pack(fill=tk.X)
        tk.Label(tilt_header, text="Tilt Joint (Vertical):", font=("DejaVu Sans", 9, "bold")).pack(side=tk.LEFT)
        self.tilt_val_lbl = tk.Label(tilt_header, text="0.0° (0.00 rad)", font=("DejaVu Sans", 9), fg="#1565c0")
        self.tilt_val_lbl.pack(side=tk.RIGHT)

        self.tilt_scale = tk.Scale(slider_box, from_=-68.0, to=68.0, resolution=1.0, orient=tk.HORIZONTAL, variable=self.cmd_tilt_deg, showvalue=False, command=self.on_slider_change)
        self.tilt_scale.pack(fill=tk.X, pady=(2, 6))

        # Directional buttons
        pad_frame = tk.Frame(slider_box)
        pad_frame.pack(pady=4)

        btn_up = tk.Button(pad_frame, text="▲ Tilt Up", width=10, command=lambda: self.step_joint(0, 5.0))
        btn_up.grid(row=0, column=1, padx=2, pady=2)

        btn_left = tk.Button(pad_frame, text="◀ Pan Left", width=10, command=lambda: self.step_joint(-5.0, 0))
        btn_left.grid(row=1, column=0, padx=2, pady=2)

        btn_center = tk.Button(pad_frame, text="Center", width=8, bg="#eceff1", command=self.go_home)
        btn_center.grid(row=1, column=1, padx=2, pady=2)

        btn_right = tk.Button(pad_frame, text="Pan Right ▶", width=10, command=lambda: self.step_joint(5.0, 0))
        btn_right.grid(row=1, column=2, padx=2, pady=2)

        btn_down = tk.Button(pad_frame, text="▼ Tilt Down", width=10, command=lambda: self.step_joint(0, -5.0))
        btn_down.grid(row=2, column=1, padx=2, pady=2)

        # Target Click Pad (Interactive 640x480 frame scaled to 240x120)
        target_box = tk.LabelFrame(self.root, text=" 🎯 Interactive Target Point (Click / Drag to Aim) ", font=("DejaVu Sans", 10, "bold"), padx=8, pady=4)
        target_box.pack(fill=tk.X, padx=14, pady=4)

        tk.Label(target_box, text="Click inside box to aim camera target (Switches to Track mode):", font=("DejaVu Sans", 8), fg="#555555").pack()
        self.canvas_w = 280
        self.canvas_h = 130
        self.canvas = tk.Canvas(target_box, width=self.canvas_w, height=self.canvas_h, bg="#111827", highlightthickness=1, highlightbackground="#374151")
        self.canvas.pack(pady=4)

        # Center crosshair
        cx, cy = self.canvas_w // 2, self.canvas_h // 2
        self.canvas.create_line(cx - 15, cy, cx + 15, cy, fill="#4b5563", dash=(2, 2))
        self.canvas.create_line(cx, cy - 15, cx, cy + 15, fill="#4b5563", dash=(2, 2))
        self.target_dot = self.canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill="#ef4444", outline="#ffffff")

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_click)

        # Live telemetry footer
        footer = tk.Frame(self.root, bg="#f1f5f9", pady=6, relief=tk.SUNKEN, bd=1)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        self.telemetry_lbl = tk.Label(footer, textvariable=self.actual_readout_var, font=("Monospace", 9, "bold"), fg="#1e293b", bg="#f1f5f9")
        self.telemetry_lbl.pack()

    def _bind_keys(self):
        self.root.bind("<Left>", lambda e: self.step_joint(-3.0, 0))
        self.root.bind("<Right>", lambda e: self.step_joint(3.0, 0))
        self.root.bind("<Up>", lambda e: self.step_joint(0, 3.0))
        self.root.bind("<Down>", lambda e: self.step_joint(0, -3.0))
        self.root.bind("<space>", lambda e: self.set_mode('stop'))
        self.root.bind("<h>", lambda e: self.go_home())
        self.root.bind("<H>", lambda e: self.go_home())

    def set_mode(self, mode_name):
        self.node.set_mode(mode_name)
        self.mode_var.set(mode_name.upper())
        colors = {
            'manual': ('#1976d2', '#e3f2fd'),
            'demo': ('#e65100', '#fff3e0'),
            'track': ('#00796b', '#e0f2f1'),
            'home': ('#388e3c', '#e8f5e9'),
            'stop': ('#d32f2f', '#ffebee')
        }
        fg, bg = colors.get(mode_name.lower(), ('#333333', '#ffffff'))
        self.status_lbl.config(fg=fg, bg=bg)

    def on_slider_change(self, _=None):
        if self.mode_var.get() != 'MANUAL':
            self.set_mode('manual')
        pan_deg = self.cmd_pan_deg.get()
        tilt_deg = self.cmd_tilt_deg.get()
        pan_rad = math.radians(pan_deg)
        tilt_rad = math.radians(tilt_deg)
        self.pan_val_lbl.config(text=f"{pan_deg:.1f}° ({pan_rad:.2f} rad)")
        self.tilt_val_lbl.config(text=f"{tilt_deg:.1f}° ({tilt_rad:.2f} rad)")
        self.node.send_manual_joint(pan_rad, tilt_rad)

    def step_joint(self, d_pan, d_tilt):
        new_pan = max(-160.0, min(160.0, self.cmd_pan_deg.get() + d_pan))
        new_tilt = max(-68.0, min(68.0, self.cmd_tilt_deg.get() + d_tilt))
        self.cmd_pan_deg.set(new_pan)
        self.cmd_tilt_deg.set(new_tilt)
        self.on_slider_change()

    def go_home(self):
        self.cmd_pan_deg.set(0.0)
        self.cmd_tilt_deg.set(0.0)
        self.on_slider_change()
        self.set_mode('home')

    def on_canvas_click(self, event):
        x = max(0, min(self.canvas_w, event.x))
        y = max(0, min(self.canvas_h, event.y))
        self.canvas.coords(self.target_dot, x - 5, y - 5, x + 5, y + 5)
        # Map canvas (280x130) to 640x480 pixel space
        px = (x / self.canvas_w) * 640.0
        py = (y / self.canvas_h) * 480.0
        self.set_mode('track')
        self.node.send_target_pixel(px, py)

    def _start_periodic_update(self):
        act_pan_deg = math.degrees(self.node.actual_pan)
        act_tilt_deg = math.degrees(self.node.actual_tilt)
        self.actual_readout_var.set(
            f"Actual Measured: Pan: {act_pan_deg:+.1f}° ({self.node.actual_pan:+.2f} rad) | Tilt: {act_tilt_deg:+.1f}° ({self.node.actual_tilt:+.2f} rad)"
        )
        self.root.after(50, self._start_periodic_update)

def main():
    rclpy.init()
    node = PanTiltGuiNode()

    # Spin ROS 2 in background daemon thread
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()

    root = tk.Tk()
    app = PanTiltApp(root, node)

    try:
        root.mainloop()
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

