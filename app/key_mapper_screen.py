from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QInputDialog
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QRect, QPoint, QTimer
import cv2
import json

from app.theme import apply_theme


class KeyMapperScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Key Mapper")
        self.layout = QVBoxLayout(self)

        self.image_label = DrawLabel(self)
        self.image_label.setFixedSize(1280, 720)
        self.layout.addWidget(self.image_label)

        self.capture_btn = QPushButton("Capture Screenshot")
        self.capture_btn.clicked.connect(self.capture_screenshot)
        self.layout.addWidget(self.capture_btn)

        self.save_btn = QPushButton("Save Keys")
        self.save_btn.clicked.connect(self.save_coords)
        self.save_btn.setEnabled(False)
        self.layout.addWidget(self.save_btn)

        self.undo_btn = QPushButton("Undo")
        self.undo_btn.clicked.connect(self.image_label.undo_last_box)
        self.undo_btn.setEnabled(False)
        self.layout.addWidget(self.undo_btn)

        # Setup webcam preview at 1280x720
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_preview)
        self.timer.start(30)

        apply_theme(self)

    def update_preview(self):
        ret, frame = self.cap.read()
        if ret:
            self.image_label.show_preview_frame(frame)

    def capture_screenshot(self):
        ret, frame = self.cap.read()
        if ret:
            self.timer.stop()
            self.cap.release()
            self.cap = None
            self.image_label.set_final_frame(frame)
            self.capture_btn.setEnabled(False)
            self.save_btn.setEnabled(True)
            self.undo_btn.setEnabled(True)

    def save_coords(self):
        coords = self.image_label.key_coords
        with open("assets/keys.json", "w") as f:
            json.dump(coords, f, indent=4)
        print("Saved key coordinates.")
        self.main_window.go_to_confirm_screen()


class DrawLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.preview_pixmap = None
        self.final_pixmap = None
        self.drawing = False
        self.start_point = None
        self.end_point = None
        self.rects = []
        self.key_coords = {}

    def undo_last_box(self):
        if self.rects:
            rect, label = self.rects.pop()
            if label in self.key_coords:
                del self.key_coords[label]
            self.update()

    def show_preview_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        qt_image = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
        self.preview_pixmap = QPixmap.fromImage(qt_image)
        self.setPixmap(self.preview_pixmap)

    def set_final_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        qt_image = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
        self.final_pixmap = QPixmap.fromImage(qt_image)
        self.setPixmap(self.final_pixmap)

    def mousePressEvent(self, event):
        if self.final_pixmap:
            self.drawing = True
            self.start_point = event.pos()

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.drawing:
            self.drawing = False
            self.end_point = event.pos()
            rect = QRect(self.start_point, self.end_point).normalized()
            label, ok = QInputDialog.getText(self, "Label Key", "Enter key label")
            if ok and label:
                self.rects.append((rect, label))
                self.key_coords[label] = [rect.left(), rect.top(), rect.right(), rect.bottom()]
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        base = self.final_pixmap if self.final_pixmap else self.preview_pixmap
        if base:
            painter = QPainter(self)
            painter.drawPixmap(self.rect(), base)

            if self.final_pixmap:
                pen = QPen(Qt.red, 2, Qt.SolidLine)
                painter.setPen(pen)

                for rect, label in self.rects:
                    painter.drawRect(rect)
                    painter.drawText(rect.topLeft() + QPoint(5, -5), label)

                if self.drawing and self.start_point and self.end_point:
                    temp_rect = QRect(self.start_point, self.end_point).normalized()
                    painter.drawRect(temp_rect)
