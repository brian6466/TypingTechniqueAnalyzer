from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
import cv2
import mediapipe as mp
import math
from app.util.config_manager import load_config
from app.theme import apply_theme, get_finger_color

SHIFT_KEYS = {
    "!": "1", "@": "2", "#": "3", "$": "4", "%": "5", "^": "6", "&": "7", "*": "8",
    "(": "9", ")": "0", "_": "-", "+": "=", ":": ";", "\"": "'", "?": "/", "~": "`"
}

class FingerTrackingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Finger Tracking")
        self.setFixedSize(1280, 720)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.setLayout(self.layout)

        self.video_label = QLabel()
        self.video_label.setFixedSize(1272, 712)
        self.layout.addWidget(self.video_label)

        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.mp_draw = mp.solutions.drawing_utils

        self.target_key_label = None
        self.expected_finger = None
        self.key_data = load_config("keys")
        self.technique_map = load_config("technique")

        apply_theme(self)

    FINGER_LANDMARKS = {
        "Thumb": [1, 2, 3, 4],
        "Index": [5, 6, 7, 8],
        "Middle": [9, 10, 11, 12],
        "Ring": [13, 14, 15, 16],
        "Pinky": [17, 18, 19, 20],
    }

    def set_target_keys(self, key_labels):
        self.target_key_labels = key_labels if isinstance(key_labels, list) else [key_labels]

    def get_finger_that_pressed_key(self, key_label):
        if key_label not in self.key_data:
            print(f"Key '{key_label}' not found.")
            return None

        x1, y1, x2, y2 = self.key_data[key_label]
        key_center = ((x1 + x2) // 2, (y1 + y2) // 2)

        ret, frame = self.cap.read()
        if not ret:
            return None

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        if not results.multi_hand_landmarks or not results.multi_handedness:
            return None

        h, w, _ = frame.shape
        closest_finger = None
        min_distance = float("inf")

        for hand_landmarks, hand_handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            raw_label = hand_handedness.classification[0].label
            hand_label = "Left" if raw_label == "Right" else "Right"

            for tip_idx, name in {4: "Thumb", 8: "Index", 12: "Middle", 16: "Ring", 20: "Pinky"}.items():
                lm = hand_landmarks.landmark[tip_idx]
                fx, fy = int(lm.x * w), int(lm.y * h)
                dist = math.hypot(fx - key_center[0], fy - key_center[1])
                if dist < min_distance:
                    min_distance = dist
                    closest_finger = "Thumb" if name == "Thumb" else f"{hand_label} {name}"

        return closest_finger

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, hand_handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                raw_label = hand_handedness.classification[0].label
                hand_label = "Left" if raw_label == "Right" else "Right"

                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                h, w, _ = frame.shape
                finger_nodes = set()

                for finger_name, indices in self.FINGER_LANDMARKS.items():
                    finger_label = "Thumb" if finger_name == "Thumb" else f"{hand_label} {finger_name}"
                    color = get_finger_color(finger_label)

                    for idx in indices:
                        lm = hand_landmarks.landmark[idx]
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        cv2.circle(frame, (cx, cy), 5, color, -1)
                        finger_nodes.add(idx)

                for idx in range(21):
                    if idx not in finger_nodes:
                        lm = hand_landmarks.landmark[idx]
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        cv2.circle(frame, (cx, cy), 5, (255, 255, 255), -1)

        if self.target_key_labels:
            for key in self.target_key_labels:
                if key not in self.key_data:
                    continue
                x1, y1, x2, y2 = self.key_data[key]
                finger = self.technique_map.get(key, "Unknown")
                if isinstance(finger, list):
                    finger = finger[0]
                color = get_finger_color(finger)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        qt_img = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_img))

    def closeEvent(self, event):
        self.cap.release()
        event.accept()
