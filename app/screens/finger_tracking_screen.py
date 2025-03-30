from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
import cv2
import mediapipe as mp

from app.theme import apply_theme


class FingerTrackingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mediapipe Hands Tracking")
        self.setFixedSize(1280, 720)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.setLayout(self.layout)

        self.video_label = QLabel()
        self.video_label.setFixedSize(1272, 712)
        self.layout.addWidget(self.video_label)

        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.mp_draw = mp.solutions.drawing_utils

        apply_theme(self)

    def get_finger_that_pressed_key(self, key_label):
        import json
        import os
        import math

        keys_path = "app/assets/keys.json"
        if not os.path.exists(keys_path):
            print("Key locations not found.")
            return None

        with open(keys_path, "r") as f:
            key_data = json.load(f)

        if key_label not in key_data:
            print(f"Key '{key_label}' not found.")
            return None

        x1, y1, x2, y2 = key_data[key_label]
        key_center = ((x1 + x2) // 2, (y1 + y2) // 2)

        ret, frame = self.cap.read()
        if not ret:
            return None

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        if not results.multi_hand_landmarks or not results.multi_handedness:
            return None

        h, w, _ = frame.shape

        fingertip_ids = {
            4: "Thumb",
            8: "Index",
            12: "Middle",
            16: "Ring",
            20: "Pinky"
        }

        closest_finger = None
        min_distance = float("inf")

        for hand_landmarks, hand_handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            # hands seemed to be mirrored so here is a quick fix
            raw_label = hand_handedness.classification[0].label
            hand_label = "Left" if raw_label == "Right" else "Right"

            for idx, finger_name in fingertip_ids.items():
                lm = hand_landmarks.landmark[idx]
                fx, fy = int(lm.x * w), int(lm.y * h)

                dist = math.hypot(fx - key_center[0], fy - key_center[1])
                if dist < min_distance:
                    min_distance = dist
                    closest_finger = f"{hand_label} {finger_name}"

        return closest_finger

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_img))

    def closeEvent(self, event):
        self.cap.release()
        event.accept()
