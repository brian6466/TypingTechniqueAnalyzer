from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QTextEdit
from PyQt5.QtCore import Qt
from app.theme import apply_theme


class ResultScreen(QWidget):
    def __init__(self, main_window, time_taken=0.0, accuracy=100.0, finger_stats=None):
        super().__init__()
        self.main_window = main_window
        self.finger_stats = finger_stats or {}

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.result_label = QLabel()
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 24px;")
        layout.addWidget(self.result_label)

        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        self.stats_display.setStyleSheet("font-size: 16px; background-color: #f0f0f0;")
        layout.addWidget(self.stats_display)

        self.new_test_btn = QPushButton("Start New Test")
        self.new_test_btn.setFixedWidth(200)
        self.new_test_btn.clicked.connect(self.start_new_test)
        layout.addWidget(self.new_test_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)
        self.update_results(time_taken, accuracy)

        apply_theme(self)

    def update_results(self, wpm, accuracy):
        summary = f"Typing Test Complete!\n\nWPM: {wpm}\nAccuracy: {accuracy:.1f}%"
        self.result_label.setText(summary)

        if self.finger_stats:
            stats_text = "\n\nKey-by-Key Finger Accuracy:\n\n"
            for key, entries in self.finger_stats.items():
                for entry in entries:
                    used = entry.get("used") or "Unknown"
                    expected = entry.get("expected") or "N/A"
                    result = "Correct" if entry.get("correct") else "Incorrect"
                    stats_text += f"{key}: {result} Used: {used} | Expected: {expected}\n"

            self.stats_display.setPlainText(stats_text)
        else:
            self.stats_display.setPlainText("No finger data was recorded.")

    def start_new_test(self):
        self.main_window.typing_test_screen.reset_test()
        self.main_window.stack.setCurrentWidget(self.main_window.typing_test_screen)
