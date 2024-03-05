import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtGui import QPalette, QColor
from PyQt6 import uic
from LogIn_UI import Ui_MainWindow


class MainWindow():
    def __init__(self):
        self.main_win = QMainWindow()
        self.uic = Ui_MainWindow()
        self.uic.setupUi(self.main_win)
        self.uic.pushButton.clicked.connect(self.showtext)  # Push button define

    def showtext(self):
        self.uic.Password.setText("Jack Sparrow join the chat") 
        self.uic.Email.setText("Jack Hollow fuck you all")

    def show(self):
        self.main_win.show()

if __name__ =="__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())

