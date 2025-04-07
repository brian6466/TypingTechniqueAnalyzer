from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt5.QtCore import Qt
from app.theme import apply_theme


class ResultScreen(QWidget):
    def __init__(self, main_window, wpm=0, accuracy=100.0, finger_stats=None):
        super().__init__()
        self.main_window = main_window
        self.finger_stats = finger_stats or {}

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        # Header
        summary_label = QLabel(f"Typing Test Complete!\n\nWPM: {wpm}    Accuracy: {accuracy:.1f}%")
        summary_label.setAlignment(Qt.AlignCenter)
        summary_label.setStyleSheet("font-size: 20px;")
        layout.addWidget(summary_label)

        # Finger breakdown area (no background override)
        self.stats_box = QTextEdit()
        self.stats_box.setReadOnly(True)
        self.stats_box.setStyleSheet("font-size: 14px; border: none;")
        layout.addWidget(self.stats_box)

        self.display_finger_stats()

        # Restart button
        restart_btn = QPushButton("Start New Test")
        restart_btn.setFixedWidth(200)
        restart_btn.clicked.connect(self.start_new_test)
        layout.addWidget(restart_btn, alignment=Qt.AlignCenter)

        apply_theme(self)

    def display_finger_stats(self):
        if not self.finger_stats:
            self.stats_box.setPlainText("No finger usage data was recorded.")
            return

        all_fingers = [
            "Left Pinky", "Left Ring", "Left Middle", "Left Index", "Left Thumb",
            "Right Thumb", "Right Index", "Right Middle", "Right Ring", "Right Pinky"
        ]

        finger_summary = {
            finger: {
                "correct": 0,
                "incorrect": 0,
                "correct_keys": [],
                "incorrect_keys": []
            } for finger in all_fingers
        }

        total_correct = 0
        total_attempts = 0

        # Collect stats
        for key, entries in self.finger_stats.items():
            for entry in entries:
                finger = str(entry.get("used") or "Unknown")
                correct = entry.get("correct", False)

                if finger not in finger_summary:
                    continue

                if correct:
                    finger_summary[finger]["correct"] += 1
                    finger_summary[finger]["correct_keys"].append(key)
                    total_correct += 1
                else:
                    finger_summary[finger]["incorrect"] += 1
                    finger_summary[finger]["incorrect_keys"].append(key)

                total_attempts += 1

        overall_accuracy = (total_correct / total_attempts) * 100 if total_attempts else 0

        output = [
            f"Technique Accuracy: {overall_accuracy:.1f}%"
        ]

        def format_finger_block(finger):
            stats = finger_summary[finger]
            correct = stats["correct"]
            incorrect = stats["incorrect"]
            total = correct + incorrect
            correct_keys = ", ".join(sorted(set(stats["correct_keys"]))) or "None"
            incorrect_keys = ", ".join(sorted(set(stats["incorrect_keys"]))) or "None"

            if total == 0:
                return f"{finger}\n  Correct 0 (None)  Incorrect 0 (None)\n  Accuracy: N/A\n"
            else:
                acc = (correct / total) * 100
                return f"{finger}\n  Correct {correct} ({correct_keys})  Incorrect {incorrect} ({incorrect_keys})\n  Accuracy: {acc:.1f}%\n"

        left_row = [format_finger_block(f) for f in all_fingers[:5]]
        right_row = [format_finger_block(f) for f in all_fingers[5:]]

        output.append("\n".join(left_row))
        output.append("\n" + "-" * 80 + "\n")
        output.append("\n".join(right_row))

        self.stats_box.setPlainText("\n".join(output))

    def start_new_test(self):
        self.main_window.typing_test_screen.reset_test()
        self.main_window.stack.setCurrentWidget(self.main_window.typing_test_screen)
