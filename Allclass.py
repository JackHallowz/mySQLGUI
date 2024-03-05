from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem , QLineEdit, QDialog, QMessageBox, QFileDialog
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QFont

class myMessBox(QMessageBox):
    def __init__(self, txt:str, title:str, icon:str, parent=None):
        super(myMessBox, self).__init__(parent)
        self.setText(txt)
        self.setWindowTitle(title)
        match icon:
            case "Warning":
                self.setIcon(QMessageBox.Icon.Warning)
            case "Critical":
                self.setIcon(QMessageBox.Icon.Critical)
            case "Information":
                self.setIcon(QMessageBox.Icon.Information)
            case "Question":
                self.setIcon(QMessageBox.Icon.Question)
            case _:
                self.setIcon(QMessageBox.Icon.NoIcon)
        self.exec()

class StandardItem(QStandardItem):
    def __int__(self, txt='', font_size=15, set_bold=True):
        super().__init__()
        fnt = QFont()
        fnt.setPointSize(font_size)
        fnt.setBold(set_bold)
        self.setEditable(False)
        self.setText(txt)
        self.setFont(fnt)
        self.isEditable(False)