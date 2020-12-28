from PyQt5.QtWidgets import QLineEdit


class LineEdit(QLineEdit):
    def __init__(self, parent, **kwargs):
        super(LineEdit, self).__init__(parent, **kwargs)
        self.setToolTip(self.text())
        self.textChanged.connect(self.onTextChanged)

    def onTextChanged(self, text):
        self.setToolTip(text)
