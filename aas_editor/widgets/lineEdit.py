#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/

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
