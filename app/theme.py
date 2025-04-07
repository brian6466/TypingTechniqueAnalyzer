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
    "Left Pinky":    (255, 100, 100),   # Bright Red
    "Left Ring":     (80, 180, 255),    # Bright Blue
    "Left Middle":   (100, 255, 100),   # Bright Green
    "Left Index":    (255, 220, 100),   # Bright Amber
    "Left Thumb":    (200, 100, 255),   # Bright Purple

    "Right Thumb":   (200, 100, 255),   # Bright Purple
    "Right Index":   (100, 255, 255),   # Bright Cyan
    "Right Middle":  (230, 255, 100),   # Bright Lime
    "Right Ring":    (160, 110, 90),    # Warmer Brown
    "Right Pinky":   (100, 120, 255),   # Brighter Indigo
}


def get_finger_color(finger_label):
    return FINGER_COLORS.get(finger_label, (255, 255, 255))
