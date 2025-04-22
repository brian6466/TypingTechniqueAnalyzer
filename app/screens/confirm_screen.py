from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint
import cv2
from ultralytics import YOLO

from app.theme import apply_theme
from app.util.config_manager import load_config, save_config


class ConfirmScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.image_label = QLabel()
        self.image_label.setFixedSize(1280, 720)
        self.image_label.setStyleSheet("background-color: black;")
        self.layout.addWidget(self.image_label)

        self.loading_label = QLabel("Loading camera...")
        self.loading_label.setStyleSheet("font-size: 24px; color: white; background-color: black;")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.loading_label)

        option_layout = QHBoxLayout()

        self.use_existing_yolo_btn = QPushButton("YOLO")
        self.use_existing_yolo_btn.clicked.connect(self.load_yolo_mapping)

        self.generate_yolo_btn = QPushButton("YOLO Mapping")
        self.generate_yolo_btn.clicked.connect(self.generate_yolo_keymap)

        self.manual_btn = QPushButton("Manual Mapping")
        self.manual_btn.clicked.connect(self.manual_keymap)

        option_layout.addWidget(self.use_existing_yolo_btn)
        option_layout.addWidget(self.generate_yolo_btn)
        option_layout.addWidget(self.manual_btn)
        self.layout.addLayout(option_layout)

        button_layout = QHBoxLayout()
        self.confirm_btn = QPushButton("Continue")
        self.confirm_btn.clicked.connect(self.go_to_typing_test)

        button_layout.addWidget(self.confirm_btn)
        self.layout.addLayout(button_layout)

        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.key_coords = {}

        apply_theme(self)

    def start_camera_with_overlay(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        self.wait_for_first_frame()

    def wait_for_first_frame(self):
        ret, _ = self.cap.read()
        if ret:
            self.loading_label.hide()
            self.timer.start(30)
            self.main_window.stack.setCurrentWidget(self)
        else:
            QTimer.singleShot(100, self.wait_for_first_frame)

    def stop_camera(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None

    def update_frame(self):
        if not self.cap or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret or frame is None:
            print("Failed to read frame from webcam")
            return

        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            qt_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

            pixmap = QPixmap.fromImage(qt_img)

            painter = QPainter(pixmap)
            pen = QPen(Qt.green, 2, Qt.SolidLine)
            painter.setPen(pen)

            for label, coords in self.key_coords.items():
                try:
                    x1, y1, x2, y2 = coords
                    rect = QRect(x1, y1, x2 - x1, y2 - y1)
                    painter.drawRect(rect)
                    painter.drawText(QPoint(x1 + 5, y1 - 5), label)
                except Exception as e:
                    print(f"Error drawing label '{label}': {e}")

            painter.end()
            self.image_label.setPixmap(pixmap)
        except Exception as e:
            print("Exception in update_frame:", e)

    def load_key_coords(self):
        data = load_config("keys")
        return data

    def go_to_typing_test(self):
        self.stop_camera()
        self.main_window.go_to_typing_test_screen()

    def go_to_key_mapper(self):
        self.stop_camera()
        self.main_window.stack.setCurrentWidget(self.main_window.key_mapper_screen)

    def generate_yolo_keymap(self):
        self.stop_camera()
        self.main_window.key_mapper_screen.mapping_mode = "YOLO"
        self.main_window.stack.setCurrentWidget(self.main_window.key_mapper_screen)

    def manual_keymap(self):
        self.stop_camera()
        self.main_window.key_mapper_screen.mapping_mode = "manual"
        self.main_window.stack.setCurrentWidget(self.main_window.key_mapper_screen)

    def load_yolo_mapping(self):
        keymap_rel = load_config("keymap")

        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        ret, frame = cap.read()
        cap.release()

        model = YOLO("runs/detect/train/weights/best.pt")
        results = model(frame, conf=0.5)[0]

        for box in results.boxes:
            if model.names[int(box.cls[0])] == "keyboard":
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                abs_keys = {
                    k: [
                        int(x1 + v[0] * (x2 - x1)),
                        int(y1 + v[1] * (y2 - y1)),
                        int(x1 + v[2] * (x2 - x1)),
                        int(y1 + v[3] * (y2 - y1)),
                    ]
                    for k, v in keymap_rel.items()
                }

                save_config("keys", abs_keys)
                self.key_coords = abs_keys
                self.start_camera_with_overlay()
                return

