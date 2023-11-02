import threading
import time
from functools import partial

import rustimport.import_hook  # noqa: F401
from lane_follower import run_robot_with_theta
from utils import create_video_capture, detect_green, try_func

import ruspy


def check_user_input():
    while True:
        if ruspy.reset_user():
            global exit_flag
            exit_flag = True  # Set the exit flag to True
            break


def run_forward(secs, speed, wobble_secs=0.1):
    motors = ruspy.motors_init(50, 100)
    toggle_angle = True  # Used to alternate between 59.0 and 58.9
    _, _, ms = ruspy.servos_init()
    motors.forward(speed)

    start_time = time.time()
    while time.time() - start_time < secs:
        if toggle_angle:
            ms.angle(59.0)
            toggle_angle = False
        else:
            ms.angle(58.9)
            toggle_angle = True
        time.sleep(wobble_secs)


def main(max_time_limit=30):
    start_time = time.time()
    try:
        # max_time_limit=0 acts as infinite loop to check only exit_flag
        while not (
            max_time_limit > 0 and time.time() - start_time >= max_time_limit
        ) and not exit_flag:
            vid_cap = create_video_capture(640, 480, fps=30)
            # run_forward = partial(run_forward, secs=60, speed=100)
            run_robot = partial(
                run_robot_with_theta, secs=10, threshold=6, w=640, h=480, fps=30
            )
            print("DETECTING TRAFFIC LIGHTS")
            if detect_green(vid_cap, max_time_limit=10):
                try_func(run_robot)
            else:
                print("SORRY,  I didn't get the GREEN signal")
        ruspy.reset_mcu()
        print("ROBOT DEAD")
    except Exception as ex:
        print("An error occurred:", ex, flush=True)
        ruspy.reset_mcu()


if __name__ == "__main__":
    print("ROBOT ALIVE")
    exit_flag = False

    # Start a separate thread to periodically check user input
    input_thread = threading.Thread(target=check_user_input)
    input_thread.start()
    # Run the main code in the main thread
    main(max_time_limit=30)
    # Wait for the input thread to finish
    input_thread.join()
    if exit_flag:
        ruspy.reset_mcu()
        print("USER EXIT")
        print("ROBOT DEAD")
