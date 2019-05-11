import cv2
import numpy as np


class FrameAdapter:
    def __init__(self, resize_coef):
        self.resize_coef = resize_coef

    def process_frame(self, frame):
        if not isinstance(frame, np.ndarray):
            frame = cv2.imread(frame)

        # Resize frame of video to `resize_coef` size for faster face recognition processing
        return cv2.resize(frame, (0, 0), fx=self.resize_coef, fy=self.resize_coef)
