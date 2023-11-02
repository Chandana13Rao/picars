import time
import traceback

import cv2
import rustimport.import_hook  # noqa: F401
from traffic_light import detect_traffic_light

import ruspy


def try_func(func):
    try:
        ruspy.main_init()
        func()
    except Exception as e:
        print(f"ERROR in {func.__name__}: {e}")
        traceback.print_exc()
    finally:
        print("FINAL RESET")
        ruspy.reset_mcu()


def create_video_capture(h=224, w=224, fps=10):
    vid_cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    vid_cap.set(cv2.CAP_PROP_FRAME_WIDTH, h)
    vid_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, w)
    vid_cap.set(cv2.CAP_PROP_FPS, fps)

    return vid_cap


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
        if not detect_traffic_light(cv_image):
            continue

        # Green light detected
        return True
