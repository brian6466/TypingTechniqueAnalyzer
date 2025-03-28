from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

from app.theme import apply_theme


class ResultScreen(QWidget):
    def __init__(self, main_window, time_taken=0.0, accuracy=100.0):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.result_label = QLabel()
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 24px;")
        layout.addWidget(self.result_label)

        # 🔁 Start new test button
        self.new_test_btn = QPushButton("Start New Test")
        self.new_test_btn.setFixedWidth(200)
        self.new_test_btn.clicked.connect(self.start_new_test)
        layout.addWidget(self.new_test_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)
        self.update_results(time_taken, accuracy)

        apply_theme(self)

    def update_results(self, wpm, accuracy):
        self.result_label.setText(
            f"Typing Test Complete!\n\nWPM: {wpm}\nAccuracy: {accuracy:.1f}%"
        )

    def start_new_test(self):
        self.main_window.typing_test_screen.reset_test()
        self.main_window.stack.setCurrentWidget(self.main_window.typing_test_screen)
