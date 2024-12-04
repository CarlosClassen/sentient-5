import os
import json
import cv2
import uuid


class EmotionEngine:
    def __init__(self, settings_file=None, logger=None):
        """Initialize EmotionEngine."""
        self.settings_file = settings_file
        self.logger = logger

        self.logger.info("Initializing EmotionEngine.")
        self.settings = self.load_settings()

        self.camera_index = self.settings.get("camera_index", 0)

    def load_settings(self):
        """Load settings from a JSON file."""
        abs_path = os.path.abspath(self.settings_file)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Settings file not found: {abs_path}")
        with open(abs_path, "r") as file:
            self.logger.info(f"Loaded settings from {abs_path}")
            return json.load(file)

    def capture_image(self):
        """Capture a single frame from the webcam."""
        cam = cv2.VideoCapture(self.camera_index)
        if not cam.isOpened():
            raise RuntimeError(f"Could not access webcam at index {self.camera_index}. Check your configuration.")

        ret, frame = cam.read()
        if not ret:
            cam.release()
            raise RuntimeError("Failed to capture image from webcam.")

        img_path = f"temp_{uuid.uuid4().hex}.jpg"
        cv2.imwrite(img_path, frame)
        cam.release()
        return img_path

    def analyze_emotion(self, img_path):
        """Analyze the emotion from a captured image."""
        try:
            from deepface import DeepFace
            analysis = DeepFace.analyze(img_path, actions=["emotion"])
            dominant_emotion = analysis[0]["dominant_emotion"]
            confidence = analysis[0]["emotion"][dominant_emotion]

            # Apply confidence threshold
            if confidence < 0.6:  # Example threshold
                dominant_emotion = "neutral"

            return dominant_emotion
        except Exception as e:
            self.logger.error(f"Error analyzing emotion: {e}")
            return "neutral"  # Default to neutral in case of errors
        finally:
            if os.path.exists(img_path):
                os.remove(img_path)

    def log_emotion(self, response, emotion):
        """Log the Sentient-5 response and the detected emotion."""
        log_entry = {"sentient_response": response, "emotion": emotion}
        self.logger.info(f"Logged emotion: {log_entry}")
