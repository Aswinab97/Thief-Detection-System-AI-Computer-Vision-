import cv2
import numpy as np

class MotionDetector:
    def __init__(self, threshold=40, min_contour_area=3000, dilate_iterations=2):
        self.threshold = threshold                  # ⬆️ Raised from 25 → 40
        self.min_contour_area = min_contour_area    # ⬆️ Raised from 500 → 3000
        self.dilate_iterations = dilate_iterations
        self.background = None
        self.frame_count = 0
        self.bg_refresh_interval = 200             # 🔄 Refresh background every 200 frames

    def set_background(self, frame):
        """Convert first frame to grayscale + blur and store as background."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.background = cv2.GaussianBlur(gray, (21, 21), 0)

    def update_background(self, frame, alpha=0.02):
        """
        Slowly update background to adapt to lighting changes.
        alpha = how fast background updates (lower = slower)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        # Weighted average — slowly adapts to new background
        self.background = cv2.addWeighted(self.background, 1 - alpha, gray, alpha, 0)

    def detect(self, frame):
        """
        Detect motion in the given frame compared to background.
        Returns contours and threshold image.
        """
        self.frame_count += 1

        # Convert current frame to grayscale + blur
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # Absolute difference between background and current frame
        diff = cv2.absdiff(self.background, gray)

        # Apply threshold to get binary image
        _, thresh = cv2.threshold(diff, self.threshold, 255, cv2.THRESH_BINARY)

        # Dilate to fill in holes
        thresh = cv2.dilate(thresh, None, iterations=self.dilate_iterations)

        # Find contours
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter small contours (noise)
        motion_contours = [c for c in contours if cv2.contourArea(c) >= self.min_contour_area]

        # 🔄 Slowly update background if NO motion detected
        if len(motion_contours) == 0:
            self.update_background(frame)

        return motion_contours, thresh