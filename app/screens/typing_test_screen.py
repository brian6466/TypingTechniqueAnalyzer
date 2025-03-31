from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
import random
import html

from app.screens.finger_tracking_screen import FingerTrackingScreen
from app.theme import apply_theme
from app.util.config_manager import load_config


class TypingTestScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setFocusPolicy(Qt.StrongFocus)

        self.word_bank = [
            "cat", "dog", "apple", "banana", "table", "chair", "hello", "world", "code", "type",
            "quick", "brown", "fox", "jump", "lazy", "day", "sun", "moon", "note", "play"
        ]

        self.num_words = 40
        self.words = []
        self.typed_words = []
        self.errors = []
        self.finished_words = []
        self.current_word_index = 0
        self.timer = QTimer()
        self.elapsed = 0
        self.timer.timeout.connect(self.update_timer)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.timer_label = QLabel("0s")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 24px;")
        self.layout.addWidget(self.timer_label)

        self.text_label = QLabel()
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setWordWrap(True)
        self.text_label.setFixedHeight(180)
        self.text_label.setStyleSheet("""
            font-size: 36px;
            font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
            letter-spacing: 2px;
            line-height: 48px;
        """)
        self.layout.addWidget(self.text_label)

        self.reset_test()

        self.finger_tracking_screen = FingerTrackingScreen()
        self.finger_tracking_screen.show()

        apply_theme(self)

    def reset_test(self):
        self.words = random.choices(self.word_bank, k=self.num_words)
        self.typed_words = ["" for _ in self.words]
        self.errors = [0 for _ in self.words]
        self.finished_words = [False for _ in self.words]
        self.current_word_index = 0
        self.elapsed = 0
        self.timer_label.setText("0s")
        self.timer.stop()
        self.update_display()

    def start_timer(self):
        self.timer.start(1000)

    def update_timer(self):
        self.elapsed += 1
        self.update_wpm_display()

    def update_wpm_display(self):
        self.timer_label.setText(f"{self.elapsed}s")

    def keyPressEvent(self, event):
        if not self.timer.isActive():
            self.elapsed = 1
            self.update_wpm_display()
            self.start_timer()

        current = self.typed_words[self.current_word_index]

        if event.key() == Qt.Key_Backspace:
            if current:
                self.typed_words[self.current_word_index] = current[:-1]
                if self.errors[self.current_word_index] > 0:
                    self.errors[self.current_word_index] -= 1
            elif self.current_word_index > 0:
                if not self.finished_words[self.current_word_index - 1] or \
                   self.words[self.current_word_index - 1] != self.typed_words[self.current_word_index - 1]:
                    self.current_word_index -= 1

        elif event.key() == Qt.Key_Space:
            self.finished_words[self.current_word_index] = True
            if self.current_word_index < len(self.words) - 1:
                self.current_word_index += 1

        elif event.key() == Qt.Key_Escape:
            self.reset_test()

        else:
            char = event.text()
            if char.isalpha():
                key_label = char.upper()

                finger_used = self.finger_tracking_screen.get_finger_that_pressed_key(key_label)

                if not hasattr(self, "technique_map"):
                    self.correct_finger_map = load_config("technique") or {}

                if finger_used:
                    correct_finger = self.correct_finger_map.get(key_label)

                    if correct_finger:
                        if isinstance(correct_finger, list):
                            is_correct = finger_used in correct_finger
                        else:
                            is_correct = finger_used == correct_finger

                        result = "Correct" if is_correct else "Incorrect"
                        print(f"[{result}] Key '{key_label}' - Used: {finger_used} | Expected: {correct_finger}")
                    else:
                        print(f"[Unknown] Key '{key_label}' - Used: {finger_used} | No mapping found.")
                else:
                    print(f"[Error] Couldn't detect finger for key '{key_label}'")

                word = self.words[self.current_word_index]
                idx = len(current)

                if idx < len(word):
                    if char.lower() != word[idx]:
                        self.errors[self.current_word_index] += 1
                elif idx - len(word) < 10:
                    self.errors[self.current_word_index] += 1
                else:
                    return

                self.typed_words[self.current_word_index] += char.lower()

        if self.current_word_index == len(self.words) - 1 and \
           self.typed_words[-1] == self.words[-1]:
            self.timer.stop()
            if self.elapsed == 0:
                self.elapsed = 1
            accuracy = self.calculate_accuracy()
            wpm = self.calculate_wpm()
            self.main_window.show_result_screen(wpm, accuracy)
            return

        self.update_display()
        self.update_wpm_display()

    def update_display(self):
        words_per_line = 10
        max_lines = 3
        current_line = self.current_word_index // words_per_line
        start_line = max(0, current_line - max_lines + 1)
        start_index = start_line * words_per_line
        end_index = min(len(self.words), (start_line + max_lines) * words_per_line)

        lines = []
        line = ""

        for i in range(start_index, end_index):
            expected = self.words[i]
            typed = self.typed_words[i]
            inner_spans = ""

            for j in range(len(expected)):
                char = html.escape(expected[j])
                is_cursor = (i == self.current_word_index and j == len(typed))

                if j < len(typed):
                    if expected[j] == typed[j]:
                        style = "color:#F6FFF8;"
                    else:
                        style = "color:red;"
                    if is_cursor:
                        style += "border-bottom: 3px solid #FFD700;"
                    inner_spans += f'<span style="{style}">{char}</span>'
                elif is_cursor:
                    inner_spans += f'<span style="border-bottom: 3px solid #FFD700;">{char}</span>'
                else:
                    inner_spans += f'<span>{char}</span>'

            if len(typed) > len(expected):
                extra_chars = typed[len(expected):][:10]
                for char in extra_chars:
                    inner_spans += f'<span style="color:red;">{html.escape(char)}</span>'

            styled_word = f'<span style="margin-right: 14px;">{inner_spans}</span>&nbsp;'
            line += styled_word

            if (i + 1 - start_index) % words_per_line == 0:
                lines.append(line)
                line = ""

        if line:
            lines.append(line)

        display = "<br>".join(lines)
        self.text_label.setText(display)

    def calculate_accuracy(self):
        total_chars = 0
        correct_chars = 0

        for i, word in enumerate(self.words):
            typed = self.typed_words[i]
            for j in range(min(len(word), len(typed))):
                if word[j] == typed[j]:
                    correct_chars += 1
            total_chars += len(word)

        return round((correct_chars / total_chars) * 100, 1) if total_chars else 0.0

    def calculate_wpm(self):
        correct = 0
        for i in range(len(self.words)):
            if self.words[i] == self.typed_words[i]:
                correct += 1
        return int((correct / max(self.elapsed, 1)) * 60)
