import cv2


def create_video_capture(h=224, w=224, fps=10):
    vid_cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    vid_cap.set(cv2.CAP_PROP_FRAME_WIDTH, h)
    vid_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, w)
    vid_cap.set(cv2.CAP_PROP_FPS, fps)

    return vid_cap
