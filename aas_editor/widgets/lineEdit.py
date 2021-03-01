from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import Qt


class LineEdit(QLineEdit):
    clicked = pyqtSignal()

    def __init__(self, parent, **kwargs):
        super(LineEdit, self).__init__(parent, **kwargs)
        self.setToolTip(self.text())
        self.textChanged.connect(self.onTextChanged)

    def onTextChanged(self, text):
        self.setToolTip(text)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        else:
            super(LineEdit, self).mouseReleaseEvent(event)
