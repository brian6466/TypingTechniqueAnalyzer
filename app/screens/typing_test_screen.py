from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
import random
import html

from app.screens.mediapipe_finger_tracking_screen import MediaPipeFingerTrackingScreen
from app.screens.mmpose_finger_tracking_screen import MMPoseFingerTrackingScreen
from app.theme import apply_theme
from app.util.config_manager import load_config
from app.assets.words import WORDS


class TypingTestScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMinimumSize(1200, 400)
        self.main_window.setFixedSize(1200, 400)

        self.strict_mode = True
        HAND_TRACKING_METHOD = "MMPose"

        if HAND_TRACKING_METHOD == "mediapipe":
            self.finger_tracking_screen = MediaPipeFingerTrackingScreen()
        else:
            self.finger_tracking_screen = MMPoseFingerTrackingScreen()

        self.word_bank = WORDS

        self.num_words = 40
        self.words = []
        self.typed_words = []
        self.errors = []
        self.finished_words = []
        self.finger_stats = {}
        self.total_keystrokes = 0
        self.correct_finger_map = load_config("technique") or {}
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
        self.timer_label.setStyleSheet("""
            font-size: 36px;
            line-height: 48px;
        """)

        self.layout.addWidget(self.timer_label)

        self.text_label = QLabel()
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setWordWrap(True)
        self.text_label.setFixedHeight(180)
        self.text_label.setStyleSheet("""
            font-size: 36px;
            letter-spacing: 2px;
            line-height: 48px;
        """)
        self.layout.addWidget(self.text_label)

        self.reset_test()

        apply_theme(self)

    def reset_test(self):
        self.words = random.choices(self.word_bank, k=self.num_words)
        self.typed_words = ["" for _ in self.words]
        self.errors = [0 for _ in self.words]
        self.finished_words = [False for _ in self.words]
        self.current_word_index = 0
        self.elapsed = 0
        self.total_keystrokes = 0
        self.finger_stats = {}
        self.timer_label.setText("0")
        self.timer.stop()
        self.update_display()
        self.update_expected_finger_overlay()

    def start_timer(self):
        self.timer.start(100)

    def update_timer(self):
        self.elapsed += 100
        self.update_timer_display()

    def update_timer_display(self):
        seconds = self.elapsed // 1000
        self.timer_label.setText(f"{seconds}s")

    def keyPressEvent(self, event):
        if not self.timer.isActive():
            self.elapsed = 100
            self.update_timer_display()
            self.start_timer()

        current = self.typed_words[self.current_word_index]

        if event.key() == Qt.Key_Backspace:
            self.total_keystrokes += 1
            if current:
                self.typed_words[self.current_word_index] = current[:-1]
                if self.errors[self.current_word_index] > 0:
                    self.errors[self.current_word_index] -= 1
            elif self.current_word_index > 0:
                if not self.finished_words[self.current_word_index - 1] or \
                        self.words[self.current_word_index - 1] != self.typed_words[self.current_word_index - 1]:
                    self.current_word_index -= 1


        elif event.key() == Qt.Key_Space:
            self.total_keystrokes += 1
            self.finished_words[self.current_word_index] = True
            if self.current_word_index == len(self.words) - 1:
                self.timer.stop()
                if self.elapsed == 0:
                    self.elapsed = 1
                accuracy = self.calculate_accuracy()
                wpm = self.calculate_wpm()
                self.main_window.show_result_screen(wpm, accuracy, self.finger_stats, self.elapsed)
                return
            else:
                self.current_word_index += 1


        elif event.key() == Qt.Key_Escape:
            self.reset_test()

        else:
            char = event.text()
            if char.isalpha():
                self.total_keystrokes += 1
                key_label = char.upper()
                finger_used = self.finger_tracking_screen.get_finger_that_pressed_key(key_label)

                correct_finger = self.correct_finger_map.get(key_label)
                is_correct = False

                if finger_used:
                    if isinstance(correct_finger, list):
                        is_correct = finger_used in correct_finger
                    else:
                        is_correct = finger_used == correct_finger

                    print(
                        f"[{('Correct' if is_correct else 'Incorrect')}] Key '{key_label}' - Used: {finger_used} | Expected: {correct_finger}")
                else:
                    print(f"[Error] Couldn't detect finger for key '{key_label}'")
                    finger_used = "Unknown"

                self.finger_stats.setdefault(key_label, []).append({
                    "used": finger_used or "Unknown",
                    "expected": correct_finger or "N/A",
                    "correct": is_correct if finger_used else False
                })

                word = self.words[self.current_word_index]
                idx = len(current)

                if getattr(self, "strict_mode", False):
                    if idx < len(word) and char.lower() == word[idx] and is_correct:
                        self.typed_words[self.current_word_index] += char.lower()
                    else:
                        print("[Strict Mode] Input rejected — must match character and finger.")
                        return
                else:
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
                if self.elapsed == 0:
                    self.elapsed = 100
            accuracy = self.calculate_accuracy()
            wpm = self.calculate_wpm()
            self.main_window.show_result_screen(wpm, accuracy, self.finger_stats, self.elapsed // 1000)
            return

        self.update_display()
        self.update_expected_finger_overlay()

    def update_expected_finger_overlay(self):
        current_word = self.words[self.current_word_index]
        typed = self.typed_words[self.current_word_index]
        idx = len(typed)

        if idx == len(current_word):
            self.finger_tracking_screen.set_target_key(" ", self.correct_finger_map.get(" "))
        elif idx < len(current_word):
            key = current_word[idx].upper()
            expected_finger = self.correct_finger_map.get(key, "Unknown")
            self.finger_tracking_screen.set_target_key(key, expected_finger)
        else:
            self.finger_tracking_screen.set_target_key(None)

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
        total_typed_chars = sum(len(w) for w in self.typed_words)
        correct_chars = 0

        for i, word in enumerate(self.words):
            typed = self.typed_words[i]
            for j, char in enumerate(typed):
                if j < len(word) and char == word[j]:
                    correct_chars += 1

        return round((correct_chars / total_typed_chars) * 100, 1) if total_typed_chars > 0 else 0.0

    def calculate_wpm(self):
        total_typed_chars = sum(len(w) for w in self.typed_words)
        minutes = self.elapsed / (1000 * 60)
        return round((total_typed_chars / 5) / minutes, 1) if minutes > 0 else 0.0






