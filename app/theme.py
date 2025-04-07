def apply_theme(widget):
    widget.setStyleSheet("""
        QWidget {
            background-color: #2B3B34;
            color: #B0D4CC;
            font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
        }

        QLabel {
            color: #B0D4CC;
            font-size: 18px;
        }

        QPushButton {
            background-color: #517B64;
            color: #B0D4CC;
            padding: 6px 12px;
            border-radius: 6px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #6B9080;
        }

        QPushButton:disabled {
            background-color: #3F4F48;
            color: #B0D4CC;
            border: 1px dashed #B0D4CC;
        }
    """)

FINGER_COLORS = {
    "Left Pinky":    (244, 67, 54),    # Red
    "Left Ring":     (33, 150, 243),   # Blue
    "Left Middle":   (76, 175, 80),    # Green
    "Left Index":    (255, 193, 7),    # Amber
    "Left Thumb":    (156, 39, 176),   # Purple

    "Right Thumb":   (255, 87, 34),    # Deep Orange
    "Right Index":   (0, 188, 212),    # Cyan
    "Right Middle":  (205, 220, 57),   # Lime
    "Right Ring":    (121, 85, 72),    # Brown
    "Right Pinky":   (63, 81, 181),    # Indigo
}

def get_finger_color(finger_label):
    return FINGER_COLORS.get(finger_label, (255, 255, 255))
