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


def create_video_capture(w=224, h=224, fps=10):
    vid_cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    vid_cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    vid_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    vid_cap.set(cv2.CAP_PROP_FPS, fps)

    return vid_cap


def detect_green(vid_cap, max_time_limit):
    start_time = time.time()

    while time.time() - start_time <= max_time_limit:
        # Run till Green light is detected
        ret, cv_image = vid_cap.read()
        if not ret:
            print("FRAME NOT CAPTURED")
            continue
        is_green, t_img = detect_traffic_light(cv_image)
        cv2.imwrite(t_img, "t_img.jpg")
        if not is_green:
            continue

        return True

    print("[TRAFFIC_LIGHT]: MAX TIME LIMIT EXCEEDED")
    return False
