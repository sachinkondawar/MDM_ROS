import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/sachin/pan_tilt_sim_ws/install/pan_tilt_video_sim'
