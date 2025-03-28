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
