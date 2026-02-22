import cv2

class MotionDetector:
    def __init__(self, threshold=25, min_contour_area=500, dilate_iterations=2):
        self.threshold = threshold
        self.min_contour_area = min_contour_area
        self.dilate_iterations = dilate_iterations
        self.background = None

    def set_background(self, frame):
        """Convert first frame to grayscale + blur and store as background."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.background = cv2.GaussianBlur(gray, (21, 21), 0)

    def detect(self, frame):
        """
        Detect motion in the given frame compared to background.
        Returns contours and threshold image.
        """
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

        # Filter small contours
        motion_contours = [c for c in contours if cv2.contourArea(c) >= self.min_contour_area]

        return motion_contours, thresh