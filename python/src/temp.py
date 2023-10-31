import time

import cv2
import matplotlib.pyplot as plt
import numpy as np
from lane_detector import LaneDetector


def create_video_capture(h=224, w=224, fps=10):
    vid_cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    vid_cap.set(cv2.CAP_PROP_FRAME_WIDTH, h)
    vid_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, w)
    vid_cap.set(cv2.CAP_PROP_FPS, fps)

    return vid_cap


def run_preds(vid_cap, ld, secs=10):
    started = time.time()
    last_logged = time.time()
    frame_count = 0
    frames_missed = 0

    while (time.time() - started) < secs:
        # read frame
        ret, cv_image = vid_cap.read()
        if not ret:
            frames_missed += 1
            print(f"[{frames_missed}]: failed to read frame")
            continue

        left_poly, right_poly, left, right = ld(cv_image)
        print(f"{left_poly = } {right_poly = }\n{left.shape = } {right.shape = }")
        # log model performance
        frame_count += 1
        now = time.time()
        if now - last_logged > 1:
            print(f"{frame_count / (now-last_logged)} fps")
            last_logged = now
            frame_count = 0


def nn(ld):
    img = cv2.imread("../assests/frame.jpg")
    plt.imshow(img)
    _, _, left_probs, right_probs, lane_center = ld(img)
    line_left = ld.fit_line_v_of_u(left_probs, 0.3)
    line_right = ld.fit_line_v_of_u(right_probs, 0.3)

    return line_left, line_right, lane_center


def plot_detected_lines(ld, line_left, line_right):
    u = np.arange(0, ld.cam_geom.image_width, 1)
    v_left = line_left(u)
    v_right = line_right(u)

    plt.plot(u, v_left, color="r")
    plt.plot(u, v_right, color="b")
    plt.xlim(0, ld.cam_geom.image_width)
    plt.ylim(ld.cam_geom.image_height, 0)
    plt.show()


# vid_cap = create_video_capture()
ld = LaneDetector(image_width=640, image_height=480)

# run_preds(vid_cap, ld)
line_left, line_right, lane_center, lane_deviation = nn(ld)
print(f"Lane Center (X-coordinate): {lane_center} meters")
print(f"Lane Deviation: {lane_deviation} meters")
print(line_left, line_right)
plot_detected_lines(ld, line_left, line_right)
