from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from app.confirm_screen import ConfirmScreen
from app.key_mapper_screen import KeyMapperScreen
from app.result_screen import ResultScreen
from app.theme import apply_theme
from app.typing_test_screen import TypingTestScreen
from app.config_manager import keys_exist

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Typing Technique Detector")
        self.setGeometry(100, 100, 800, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)



        self.confirm_screen = ConfirmScreen(self)
        self.key_mapper_screen = KeyMapperScreen(self)
        self.typing_test_screen = TypingTestScreen(self)
        self.result_screen = ResultScreen(self)

        self.stack.addWidget(self.confirm_screen)     
        self.stack.addWidget(self.key_mapper_screen)
        self.stack.addWidget(self.typing_test_screen)
        self.stack.addWidget(self.result_screen)

        if keys_exist():
            self.confirm_screen.start_camera_with_overlay()
            self.stack.setCurrentIndex(0)
        else:
            self.stack.setCurrentIndex(1)

        apply_theme(self)

    def go_to_confirm_screen(self):
        self.confirm_screen.start_camera_with_overlay()
        self.stack.setCurrentWidget(self.confirm_screen)

    def show_result_screen(self, wpm, accuracy):
        self.result_screen.update_results(wpm, accuracy)
        self.stack.setCurrentWidget(self.result_screen)




