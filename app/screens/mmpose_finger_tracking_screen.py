from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
import cv2
import math
from mmpose.apis import init_model, inference_topdown
from app.util.config_manager import load_config
from app.theme import apply_theme, get_finger_color

class MMPoseFingerTrackingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MMPose Hand Tracking")
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

        config_path = "app/assets/mmpose/td-hm_hrnet-w48_8xb32-210e_coco-256x192.py"
        checkpoint_path = "app/assets/mmpose/td-hm_hrnet-w48_8xb32-210e_coco-256x192-0e67c616_20220913.pth"

        self.model = init_model(config_path, checkpoint_path, device='cuda')
        self.dataset_info = self.model.cfg.dataset_info

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

        if isinstance(expected_finger, list):
            expected_finger = expected_finger[0]

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

        results = inference_topdown(self.model, frame, [], dataset_info=self.dataset_info)
        if not results:
            return None

        keypoints = results[0]['keypoints']
        closest_finger = None
        min_distance = float("inf")

        for idx, name in self.FINGERTIP_IDS.items():
            x, y, conf = keypoints[idx]
            dist = math.hypot(x - key_center[0], y - key_center[1])
            if dist < min_distance:
                min_distance = dist
                closest_finger = f"Unknown {name}"

        return closest_finger

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        results = inference_topdown(self.model, frame, [], dataset_info=self.dataset_info)

        if results:
            for r in results:
                keypoints = r['keypoints']
                for idx, name in self.FINGERTIP_IDS.items():
                    x, y, conf = keypoints[idx]
                    if conf > 0.4:
                        color = get_finger_color(f"Unknown {name}")
                        cv2.circle(frame, (int(x), int(y)), 5, color, -1)

        if self.target_key_label and self.target_key_label in self.key_data:
            x1, y1, x2, y2 = self.key_data[self.target_key_label]
            finger_label = self.expected_finger or "Unknown"
            color = get_finger_color(finger_label)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            text = f"{finger_label}"
            (text_width, _), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
            x = (frame.shape[1] - text_width) // 2
            y = frame.shape[0] - 30

            cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2, cv2.LINE_AA)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_img))

    def closeEvent(self, event):
        self.cap.release()
        event.accept()
