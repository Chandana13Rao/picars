import threading
import time
import traceback

import rustimport.import_hook  # noqa: F401
from lane_follower import run_robot_with_theta
from utils import create_video_capture, detect_green

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


def main(max_time_limit=0):
    fps = 30
    ruspy.main_init()
    motors = ruspy.motors_init(50, 100)
    cs1, cs2, ms = ruspy.servos_init()
    cs1.angle(-5.0)
    ms.angle(60.0)
    print("MAIN INIT SUCCESSFULL")
    try:
        vid_cap = create_video_capture(640, 480, fps=fps)
        # Discard 1st fps
        for _ in range(fps):
            _, _ = vid_cap.read()
        # run_forward = partial(run_forward, secs=60, speed=100)
        print("TRAFFIC LIGHT DETECTION STARTED")
        cs2.angle(37.0)
        if detect_green(vid_cap, max_time_limit=10):
            try:
                cs2.angle(75.0)
                # Discard 1st fps
                for _ in range(fps):
                    _, _ = vid_cap.read()
                run_robot_with_theta(vid_cap, motors, ms, exit_flag, max_time_limit, 6)
            except Exception as e:
                print(f"ERROR in run_robot_with_theta: {e}")
                traceback.print_exc()
                ruspy.reset_mcu()
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
    main(0)
    # Wait for the input thread to finish
    input_thread.join()
    if exit_flag:
        ruspy.reset_mcu()
        print("USER EXIT")
        print("ROBOT DEAD")
