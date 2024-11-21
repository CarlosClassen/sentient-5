import cv2
from deepface import DeepFace
import json
import os
import uuid


class EmotionEngine:
    def __init__(self, log_file="emotion_log.json"):
        """Initialize the EmotionEngine with a log file path."""
        self.log_file = log_file  # Path to the emotion log file
        self.log = []  # In-memory log for detected emotions

    def capture_image(self):
        """Capture a single frame from the webcam."""
        cam = cv2.VideoCapture(0)  # Open the default webcam
        if not cam.isOpened():
            raise RuntimeError("Could not access the webcam.")

        ret, frame = cam.read()
        if not ret:
            cam.release()
            raise RuntimeError("Failed to capture image from webcam.")

        # Save the captured frame as a temporary image
        img_path = f"temp_{uuid.uuid4().hex}.jpg"  # Generate a unique filename
        cv2.imwrite(img_path, frame)
        cam.release()
        return img_path

    def analyze_emotion(self, img_path):
        """Analyze the emotion from a captured image."""
        try:
            # Perform emotion analysis using DeepFace
            analysis = DeepFace.analyze(img_path, actions=["emotion"])
            dominant_emotion = analysis[0]["dominant_emotion"]  # Extract the dominant emotion
            return dominant_emotion
        except Exception as e:
            print(f"Error analyzing emotion: {e}")
            return None
        finally:
            # Clean up the temporary image file
            if os.path.exists(img_path):
                os.remove(img_path)

    def log_emotion(self, response, emotion):
        """Log the Sentient-5 response and the detected emotion."""
        log_entry = {
            "sentient_response": response,
            "emotion": emotion
        }
        self.log.append(log_entry)

        # Write the log to the file
        with open(self.log_file, "w") as file:
            json.dump(self.log, file, indent=4)

    def load_existing_log(self):
        """Load an existing log file, if it exists."""
        if os.path.exists(self.log_file):
            with open(self.log_file, "r") as file:
                self.log = json.load(file)
