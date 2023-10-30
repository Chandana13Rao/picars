import time

import rustimport.import_hook  # noqa: F401
from traffic_light import detect
from utils import create_video_capture

import ruspy


def detect_green(vid_cap, max_time_limit):
    start_time = time.time()

    while True:
        # Check Max time limit
        if time.time() - start_time >= max_time_limit:
            print("MAX TIME LIMIT EXCEEDED")
            return False

        # Run till Green light is detected
        ret, cv_image = vid_cap.read()
        if not ret:
            print("FRAME NOT CAPTURED")
            continue
        if not detect(cv_image):
            continue

        # Green light detected
        return True


def run_forward(secs, speed):
    motors = ruspy.motors_init(50, 100)
    motors.forward(speed)
    time.sleep(secs)


if __name__ == "__main__":
    vid_cap = create_video_capture(h=480, w=640, fps=30)
    if detect_green(vid_cap, max_time_limit=10):
        run_forward(secs=10, speed=100)
    else:
        print("SORRY,  I didn't get the GREEN signal")
