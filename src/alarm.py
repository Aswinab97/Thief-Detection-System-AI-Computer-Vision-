import cv2
from datetime import datetime

class Alarm:
    def __init__(self):
        self.triggered = False

    def trigger(self, frame):
        """Mark alarm as triggered and print alert."""
        self.triggered = True
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[ALERT] 🚨 Intruder detected at {timestamp}")

    def reset(self):
        """Reset alarm state."""
        self.triggered = False