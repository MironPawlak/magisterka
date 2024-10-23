import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide6.QtCore import Slot
from old.ui_mainwindow import Ui_MainWindow


@Slot()
def say_hello():
    print("Button clicked, Hello!")


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    button = QPushButton("Click me")
    button.clicked.connect(say_hello)
    button.show()


    sys.exit(app.exec())
