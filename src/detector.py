import cv2
import time
from datetime import datetime
from src.motion import MotionDetector
from src.alarm import Alarm

class ThiefDetector:
    def __init__(self, output_path="output/recordings/recording.mp4"):
        self.motion_detector = MotionDetector()
        self.alarm = Alarm()
        self.output_path = output_path
        self.writer = None
        self.cap = None

    def _init_writer(self, frame):
        """Initialize video writer based on frame size."""
        h, w = frame.shape[:2]
        # ✅ mp4v codec — works natively on Mac with QuickTime
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(self.output_path, fourcc, 20.0, (w, h))
        print(f"🎥 Recording to: {self.output_path}")

    def _draw_status(self, frame, is_unsafe):
        """Draw SAFE/UNSAFE label and timestamp on frame."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if is_unsafe:
            label = "UNSAFE"
            color = (0, 0, 255)   # Red
        else:
            label = "SAFE"
            color = (0, 255, 0)   # Green

        # Status text top-right
        cv2.putText(frame, label, (450, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

        # Timestamp bottom-left
        cv2.putText(frame, timestamp, (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        return frame

    def _list_all_cameras(self):
        """List all available cameras with their names."""
        print("\n📷 Available cameras:")
        for index in range(5):
            cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
            if cap.isOpened():
                print(f"   [{index}] Camera found at index {index}")
                cap.release()
        print()

    def _open_builtin_camera(self):
        """
        Open the MacBook built-in FaceTime HD camera.
        On Mac with Continuity Camera disabled, index 0 = built-in.
        We explicitly use CAP_AVFOUNDATION backend.
        """
        self._list_all_cameras()

        for index in [0, 1, 2]:
            print(f"🔍 Trying camera index {index} with AVFoundation...")
            cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)

            if not cap.isOpened():
                print(f"   ❌ Index {index} failed to open")
                cap.release()
                continue

            # Warm up — discard black frames
            for _ in range(20):
                cap.read()

            ret, frame = cap.read()
            if ret and frame is not None and frame.mean() > 2.0:
                print(f"   ✅ Index {index} working! (brightness={frame.mean():.1f})")
                return cap, index

            print(f"   ⚠️  Index {index} opened but frame is black (brightness={frame.mean() if frame is not None else 'N/A'})")
            cap.release()

        return None, -1

    def run(self):
        """Main detection loop."""
        print("🔍 Looking for built-in MacBook camera...")
        self.cap, cam_index = self._open_builtin_camera()

        if self.cap is None:
            print("\n❌ No working camera found!")
            print("👉 Try these steps:")
            print("   1. Disable Continuity Camera: iPhone → Settings → General → AirPlay & Continuity → OFF")
            print("   2. Disconnect iPhone from Mac")
            print("   3. Run again")
            return

        print(f"✅ Using camera index {cam_index}. Press 'q' or ESC to quit.")

        # Final warm-up
        print("⏳ Final camera warm-up...")
        for _ in range(20):
            self.cap.read()
        time.sleep(0.5)

        # Grab background frame
        ret, first_frame = self.cap.read()
        if not ret or first_frame is None:
            print("❌ Failed to grab first frame")
            self.cap.release()
            return

        self.motion_detector.set_background(first_frame)
        self._init_writer(first_frame)
        print("📸 Background captured. Monitoring started...\n")

        while True:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                print("❌ Failed to read frame")
                break

            # Detect motion
            contours, _ = self.motion_detector.detect(frame)
            is_unsafe = len(contours) > 0

            # Draw bounding boxes
            for contour in contours:
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # Trigger or reset alarm
            if is_unsafe:
                self.alarm.trigger(frame)
            else:
                self.alarm.reset()

            # Overlay status + timestamp
            frame = self._draw_status(frame, is_unsafe)

            # Save frame
            self.writer.write(frame)

            # Show frame
            cv2.imshow("Thief Detector", frame)

            # Exit on 'q' or ESC
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == 27:
                print("👋 Exiting...")
                break

        self._cleanup()

    def _cleanup(self):
        """Release all resources."""
        if self.cap:
            self.cap.release()
        if self.writer:
            self.writer.release()
        cv2.destroyAllWindows()
        print("✅ Resources released. Recording saved to:", self.output_path)