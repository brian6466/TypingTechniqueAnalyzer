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
    "Left Pinky":    (255, 100, 100),
    "Left Ring":     (80, 180, 255),
    "Left Middle":   (100, 255, 100),
    "Left Index":    (255, 220, 100),

    "Thumb":    (200, 100, 255),

    "Right Index":   (100, 255, 255),
    "Right Middle":  (230, 255, 100),
    "Right Ring":    (160, 110, 90),
    "Right Pinky":   (100, 120, 255),
}


def get_finger_color(finger_label):
    return FINGER_COLORS.get(finger_label, (255, 255, 255))
