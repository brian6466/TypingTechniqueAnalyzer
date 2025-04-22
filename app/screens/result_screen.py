from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QSize
import qtawesome as qta
from PyQt5.QtCore import QSize
from app.theme import apply_theme


class ResultScreen(QWidget):
    def __init__(self, main_window, wpm=0, accuracy=100.0, finger_stats=None, time_taken=0):
        super().__init__()
        self.main_window = main_window
        self.finger_stats = finger_stats or {}
        self.time_taken = time_taken

        self.technique_accuracy = self.calculate_technique_accuracy()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        self.setLayout(layout)

        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(80)
        layout.addLayout(metrics_layout)

        def create_metric_block(title, value):
            container = QVBoxLayout()
            container.setSpacing(0)
            container.setAlignment(Qt.AlignCenter)

            label = QLabel(title)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-size: 24px;")

            val = QLabel(value)
            val.setAlignment(Qt.AlignCenter)
            val.setStyleSheet("font-size: 32px; font-weight: bold; margin-top: -8px;")

            container.addWidget(label)
            container.addWidget(val)
            return container

        metrics_layout.addLayout(create_metric_block("WPM", f"{wpm}"))
        metrics_layout.addLayout(create_metric_block("Acc", f"{accuracy:.1f}%"))
        metrics_layout.addLayout(create_metric_block("Technique", f"{self.technique_accuracy:.1f}%"))
        metrics_layout.addLayout(create_metric_block("Time", f"{self.time_taken}s"))

        restart_btn = QPushButton()
        restart_btn.setFixedSize(50, 50)
        restart_btn.setIcon(qta.icon("fa5s.sync", color="#B0D4CC"))
        restart_btn.setIconSize(QSize(32, 32))
        restart_btn.setStyleSheet("QPushButton { border: none; background-color: transparent; }")
        restart_btn.setCursor(QCursor(Qt.PointingHandCursor))
        restart_btn.clicked.connect(self.start_new_test)
        layout.addWidget(restart_btn, alignment=Qt.AlignCenter)

        self.print_finger_stats()

        apply_theme(self)

    def calculate_technique_accuracy(self):
        total = 0
        correct = 0
        for entries in self.finger_stats.values():
            for entry in entries:
                total += 1
                if entry.get("correct"):
                    correct += 1
        return (correct / total) * 100 if total else 0.0

    def print_finger_stats(self):
        print("\n====== Finger Technique Accuracy Breakdown ======")
        for key, entries in self.finger_stats.items():
            for entry in entries:
                used = entry.get("used")
                expected = entry.get("expected")
                correct = entry.get("correct")
                print(f"Key: {key} | Used: {used} | Expected: {expected} | {'✔' if correct else '✘'}")
        print("================================================\n")

    def start_new_test(self):
        self.main_window.typing_test_screen.reset_test()
        self.main_window.stack.setCurrentWidget(self.main_window.typing_test_screen)
