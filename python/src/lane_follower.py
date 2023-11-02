import math
import signal
import sys
import time

import cv2
import numpy as np
from algo_lane_follower import (
    calc_servo_and_motor_controls,
    calc_servo_and_motor_controls_with_centerdiff,
    process_image,
)
from checks import create_video_capture, try_func
from lane_detector import LaneDetector

import ruspy

minLineLength = 5
maxLineGap = 10
lane_width = 0.36  # 36 cms


def run_robot_with_theta(secs=10):
    print("*************************************")
    print("RUNNING ROBOT WITH THETA CALCULATIONS")
    print("*************************************")
    started = time.time()
    vid_cap = create_video_capture(640, 480, 30)
    motors = ruspy.motors_init(50, 100)
    motors.speed(100, 100)
    # motors.forward(100)
    time.sleep(0.5)
    frame_number = 0

    while (time.time() - started) < secs:
        print("VIDEO CAPTURE STARTED")
        ret, frame = vid_cap.read()
        if not ret:
            print("FRAME NOT CAPTURED")
            continue
        print("FRAME CAPTURED")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 85, 85)
        lines = cv2.HoughLinesP(edged, 1, np.pi / 180, 10, minLineLength, maxLineGap)
        filename = f"out_{frame_number}.jpg"
        cv2.imwrite(filename, lines)

        if lines is None:
            print("NO LINES DETECTED")
        else:
            print("CALCULATE THETA")
            theta = 0
            for x in range(0, len(lines)):
                for x1, y1, x2, y2 in lines[x]:
                    # cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    theta += math.atan2((y2 - y1), (x2 - x1))

            print(theta)
            threshold = 6
            if theta > threshold:
                print("LEFT")
                motors.turn_left(100)
            if theta < -threshold:
                print("RIGHT")
                motors.turn_right(100)
            if abs(theta) < threshold:
                print("STRAIGHT")
                motors.forward(100)

            theta = 0

        frame_number += 1

    print("STOPPING MOTORS")
    motors.stop()


def run_robot_with_nn(secs=10):
    print("***********************************")
    print("RUNNING ROBOT WITH MACHINE LEARNING")
    print("***********************************")
    started = time.time()
    vid_cap = create_video_capture(640, 480, 2)
    ld = LaneDetector(image_width=640, image_height=480)
    # vid_cap = create_video_capture(1024, 512, 2)
    # ld = LaneDetector(image_width=1024, image_height=512)
    motors = ruspy.motors_init(50, 100)
    motors.speed(100, 100)
    # motors.forward(100)
    time.sleep(0.5)
    frame_number = 0

    # create black image to add left and right lanes
    lane_img = np.zeros((640, 480, 3), dtype=np.uint8)

    while (time.time() - started) < secs:
        print("VIDEO CAPTURE STARTED")
        ret, frame = vid_cap.read()
        if not ret:
            print("FRAME NOT CAPTURED")
            continue
        print("FRAME CAPTURED")
        _, _, left, right, _ = ld(frame)
        lane_img[left > 0.5, :] = [255, 255, 255]
        lane_img[right > 0.5, :] = [255, 255, 255]
        gray = cv2.cvtColor(lane_img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 85, 85)
        lines = cv2.HoughLinesP(edged, 1, np.pi / 180, 10, minLineLength, maxLineGap)
        filename = f"out_{frame_number}.jpg"
        cv2.imwrite(filename, lines)

        if lines is None:
            print("NO LINES DETECTED")
        else:
            print("CALCULATE THETA")
            theta = 0
            for x in range(0, len(lines)):
                for x1, y1, x2, y2 in lines[x]:
                    # cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    theta += math.atan2((y2 - y1), (x2 - x1))

            print(theta)
            threshold = 6
            if theta > threshold:
                print("LEFT")
                motors.turn_left(100)
            if theta < -threshold:
                print("RIGHT")
                motors.turn_right(100)
            if abs(theta) < threshold:
                print("STRAIGHT")
                motors.forward(100)

            theta = 0

        frame_number += 1

    print("STOPPING MOTORS")
    motors.stop()


def run_robot_with_nn_algo(secs=10):
    print("***********************************")
    print("RUNNING ROBOT WITH MACHINE LEARNING")
    print("***********************************")
    started = time.time()
    vid_cap = create_video_capture(640, 480, 2)
    ld = LaneDetector(image_width=640, image_height=480)
    # vid_cap = create_video_capture(1024, 512, 2)
    # ld = LaneDetector(image_width=1024, image_height=512)
    motors = ruspy.motors_init(50, 100)
    camera_servo_pin1, camera_servo_pin2, dir_servo_pin = ruspy.servos_init(
        [80, 50, 60]
    )
    frame_number = 0

    while (time.time() - started) < secs:
        print("VIDEO CAPTURE STARTED")
        ret, frame = vid_cap.read()
        if not ret:
            print("FRAME NOT CAPTURED")
            continue
        print("FRAME CAPTURED")
        (
            _,
            _,
            left_probs,
            right_probs,
            lane_center,
            lane_deviation,
        ) = ld(frame)

        (
            front_servo_direction,
            rear_motor_speed,
        ) = calc_servo_and_motor_controls_with_centerdiff(lane_center, 0.1)
        print(
            f"{lane_center = }\n{lane_deviation = }\n{rear_motor_speed = }\n{front_servo_direction = }"
        )

        if front_servo_direction == "left":
            dir_servo_pin.angle(45)
            motors.turn_left(rear_motor_speed)
        elif front_servo_direction == "right":
            dir_servo_pin.angle(75)
            motors.turn_right(rear_motor_speed)
        else:
            motors.forward(rear_motor_speed)

        frame_number += 1

    print("STOPPING MOTORS")
    motors.stop()


def run_robot_with_algo(secs=10):
    print("***********************************")
    print("RUNNING ROBOT WITH SIMPLE ALGORITHM")
    print("***********************************")
    started = time.time()
    vid_cap = create_video_capture(640, 480, 30)
    motors = ruspy.motors_init(50, 100)
    camera_servo_pin1, camera_servo_pin2, dir_servo_pin = ruspy.servos_init(
        [80, 50, 60]
    )
    frame_number = 0

    while (time.time() - started) < secs:
        print("VIDEO CAPTURE STARTED")
        ret, frame = vid_cap.read()
        if not ret:
            print("FRAME NOT CAPTURED")
            continue
        print("FRAME CAPTURED")
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        out, left_lane, right_lane, curverad, center_diff = process_image(img)
        filename = f"out_{frame_number}.jpg"
        cv2.imwrite(filename, out)

        front_servo_direction, rear_motor_speed = calc_servo_and_motor_controls(
            curverad, center_diff
        )
        print(
            f"{center_diff = }\n{curverad = }\n{rear_motor_speed = }\n{front_servo_direction = }"
        )

        if front_servo_direction == "left":
            dir_servo_pin.angle(45)
            motors.turn_left(rear_motor_speed)
        elif front_servo_direction == "right":
            dir_servo_pin.angle(75)
            motors.turn_right(rear_motor_speed)
        else:
            motors.forward(rear_motor_speed)

        frame_number += 1


class KeyboardInterruptError(Exception):
    pass


def signal_handler(sig, frame):
    raise KeyboardInterruptError("Ctrl+C pressed. Exiting...")


if __name__ == "__main__":
    # Set up a Ctrl+C signal handler
    signal.signal(signal.SIGINT, signal_handler)

    try:
        if len(sys.argv) < 2:
            print(
                """Usage: python lane_follower.py <run_type>
                    <run_type> can take one of following values:
                    (theta, nn, nn-algo, algo)"""
            )
            sys.exit(1)
        run_type = sys.argv[1]

        ruspy.main_init()
        if run_type == "theta":
            try_func(run_robot_with_theta)
        elif run_type == "nn":
            try_func(run_robot_with_nn)
        elif run_type == "algo":
            try_func(run_robot_with_algo)
        elif run_type == "nn-algo":
            try_func(run_robot_with_nn_algo)
        else:
            print(
                """Usage: python lane_follower.py <run_type>
                    <run_type> can take one of following values:
                    (theta, nn, nn-algo, algo)"""
            )
        ruspy.reset_mcu()
    except KeyboardInterruptError:
        ruspy.reset_mcu()
    except Exception as ex:
        print("An error occurred:", ex, flush=True)
        ruspy.reset_mcu()
