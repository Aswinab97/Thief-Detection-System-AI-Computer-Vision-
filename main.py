from src.detector import ThiefDetector

if __name__ == "__main__":
    print("🚨 Thief Detection System Starting...")
    detector = ThiefDetector(output_path="output/recordings/recording.mp4")
    detector.run()