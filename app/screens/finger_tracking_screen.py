from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
import cv2
import mediapipe as mp
import math
from app.util.config_manager import load_config



from app.theme import apply_theme, get_finger_color


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

        self.target_key_label = None
        self.expected_finger = None
        self.key_data = load_config("keys")
        self.technique_map = load_config("technique")

        apply_theme(self)

    FINGERTIP_IDS = {
        4: "Thumb",
        8: "Index",
        12: "Middle",
        16: "Ring",
        20: "Pinky"
    }

    def set_target_key(self, key_label, expected_finger=None):
        self.target_key_label = key_label
        if expected_finger is None:
            expected_finger = self.technique_map.get(key_label, "Unknown")
        self.expected_finger = expected_finger

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

            for idx, name in self.FINGERTIP_IDS.items():
                lm = hand_landmarks.landmark[idx]
                fx, fy = int(lm.x * w), int(lm.y * h)

                dist = math.hypot(fx - key_center[0], fy - key_center[1])
                if dist < min_distance:
                    min_distance = dist
                    closest_finger = f"{hand_label} {name}"

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

                for idx, name in self.FINGERTIP_IDS.items():
                    lm = hand_landmarks.landmark[idx]
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    finger_label = f"{hand_label} {name}"

                    color = get_finger_color(finger_label)
                    cv2.circle(frame, (cx, cy), 12, color, -1)

        if self.target_key_label and self.target_key_label in self.key_data:
            x1, y1, x2, y2 = self.key_data[self.target_key_label]

            finger_label = self.expected_finger or "Unknown"
            color = get_finger_color(finger_label)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            text = f"Use: {finger_label}"
            cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2, cv2.LINE_AA)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        qt_img = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_img))

    def closeEvent(self, event):
        self.cap.release()
        event.accept()
