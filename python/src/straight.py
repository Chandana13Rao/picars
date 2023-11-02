import signal
import time
from functools import partial

import rustimport.import_hook  # noqa: F401
from utils import create_video_capture, detect_green, try_func

import ruspy


class KeyboardInterruptError(Exception):
    pass


def signal_handler(sig, frame):
    raise KeyboardInterruptError("Ctrl+C pressed. Exiting...")


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


if __name__ == "__main__":
    # Set up a Ctrl+C signal handler
    signal.signal(signal.SIGINT, signal_handler)
    try:
        vid_cap = create_video_capture(640, 480, fps=30)
        run_forward = partial(run_forward, secs=60, speed=100)

        if detect_green(vid_cap, max_time_limit=10):
            try_func(run_forward)
        else:
            print("SORRY,  I didn't get the GREEN signal")
    except KeyboardInterruptError:
        ruspy.reset_mcu()
    except Exception as ex:
        print("An error occurred:", ex, flush=True)
        ruspy.reset_mcu()
