"""
services/face_recognition.py

Face detection + recognition using OpenCV only (Haar cascade + LBPH).
No dlib / CMake needed, so it installs cleanly on Windows.

Requires:  pip install opencv-contrib-python numpy
(use opencv-contrib-python, NOT opencv-python, because cv2.face lives in contrib)

Folder layout created automatically:
    data/faces/<student_id>/0001.jpg ...   <- saved by tools/enroll_faces.py
    data/trainer.yml                       <- trained LBPH model
    data/labels.json                       <- {"0": "S101", "1": "S102", ...}
"""

import json
from pathlib import Path

import cv2
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
FACES_DIR = DATA_DIR / "faces"
MODEL_PATH = DATA_DIR / "trainer.yml"
LABELS_PATH = DATA_DIR / "labels.json"

FACE_SIZE = (200, 200)

# LBPH confidence: LOWER = better match. ~40-60 is a strong match.
# Increase if real students are shown as "Unknown", decrease if strangers get matched.
CONFIDENCE_THRESHOLD = 70.0

_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


# --------------------------------------------------------------------------- #
# Detection helpers (also used by tools/enroll_faces.py)
# --------------------------------------------------------------------------- #
def detect_faces(bgr_image):
    """Return list of (x, y, w, h) face boxes found in a BGR image."""
    gray = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
    faces = _detector.detectMultiScale(
        gray, scaleFactor=1.2, minNeighbors=5, minSize=(60, 60)
    )
    return [tuple(int(v) for v in f) for f in faces]


def preprocess_face(bgr_image, box):
    """Crop, grayscale, resize and normalise lighting for one face."""
    x, y, w, h = box
    gray = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
    face = gray[y : y + h, x : x + w]
    face = cv2.resize(face, FACE_SIZE)
    return cv2.equalizeHist(face)


# --------------------------------------------------------------------------- #
# Training
# --------------------------------------------------------------------------- #
def train_model():
    """
    Train the LBPH model from every folder inside data/faces/.
    Returns (number_of_students, number_of_images).
    """
    if not FACES_DIR.exists():
        raise FileNotFoundError("No enrolled faces found. Run tools/enroll_faces.py first.")

    images, labels, label_map = [], [], {}
    for idx, student_dir in enumerate(sorted(p for p in FACES_DIR.iterdir() if p.is_dir())):
        label_map[idx] = student_dir.name
        for img_path in student_dir.glob("*.jpg"):
            img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            images.append(cv2.resize(img, FACE_SIZE))
            labels.append(idx)

    if not images:
        raise ValueError("No face images to train on.")

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(images, np.array(labels))

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    recognizer.write(str(MODEL_PATH))
    LABELS_PATH.write_text(json.dumps(label_map, indent=2))
    return len(label_map), len(images)


# --------------------------------------------------------------------------- #
# Recognition
# --------------------------------------------------------------------------- #
class FaceRecognizer:
    def __init__(self, threshold=CONFIDENCE_THRESHOLD):
        self.threshold = threshold
        self.recognizer = None
        self.labels = {}
        self._load()

    @property
    def ready(self):
        return self.recognizer is not None

    def _load(self):
        if not (MODEL_PATH.exists() and LABELS_PATH.exists()):
            return
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.recognizer.read(str(MODEL_PATH))
        self.labels = {int(k): v for k, v in json.loads(LABELS_PATH.read_text()).items()}

    def recognize(self, bgr_image):
        """
        Returns (results, annotated_rgb_image)
        results = [{"student_id": "S101" | None, "confidence": 42.1, "box": (x,y,w,h)}, ...]
        """
        if not self.ready:
            raise RuntimeError("Model not trained yet. Run tools/enroll_faces.py and train.")

        annotated = bgr_image.copy()
        results = []

        for box in detect_faces(bgr_image):
            face = preprocess_face(bgr_image, box)
            label, confidence = self.recognizer.predict(face)
            matched = confidence <= self.threshold and label in self.labels
            student_id = self.labels[label] if matched else None
            results.append(
                {"student_id": student_id, "confidence": float(confidence), "box": box}
            )

            x, y, w, h = box
            color = (0, 200, 0) if matched else (0, 0, 255)
            cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
            text = student_id if matched else "Unknown"
            cv2.putText(annotated, text, (x, max(y - 8, 15)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        return results, cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
