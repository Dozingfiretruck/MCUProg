from PySide6.QtWidgets import QComboBox
from PySide6 import QtCore

class QComboBox2(QComboBox):
    pop_up = QtCore.Signal()
    def showPopup(self):
        self.pop_up.emit()
        super(QComboBox2, self).showPopup()