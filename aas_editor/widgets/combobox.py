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

from typing import Optional

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QComboBox, QWidget, QLineEdit, QCompleter


class ComboBox(QComboBox):
    def __init__(self, parent: Optional[QWidget] = ...):
        super(ComboBox, self).__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)

    def wheelEvent(self, e: QtGui.QWheelEvent) -> None:
        if not self.hasFocus():
            e.ignore()
        else:
            super(ComboBox, self).wheelEvent(e)


class CompleterComboBox(ComboBox):
    def __init__(self, parent: Optional[QWidget] = ...):
        super(CompleterComboBox, self).__init__(parent)
        lineEdit = CompleterLineEdit()
        lineEdit.setObjectName("comboLine")
        lineEdit.setStyleSheet("#comboLine{border:0;}")
        self.setLineEdit(lineEdit)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        completer = self.completer()
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)


class CompleterLineEdit(QLineEdit):
    clicked = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = ...) -> None:
        if parent is ...:
            super(CompleterLineEdit, self).__init__()
        else:
            super(CompleterLineEdit, self).__init__(parent)
        self.textEdited.connect(self.onTextEdited)

    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        if a0.button() == Qt.LeftButton:
            self.clicked.emit()
            self.completer().setCompletionMode(QCompleter.UnfilteredPopupCompletion)
            self.callPopup()
        super(CompleterLineEdit, self).mouseReleaseEvent(a0)

    def onTextEdited(self):
        # force to show all items when text is empty
        if not self.text():
            self.completer().setCompletionMode(QCompleter.UnfilteredPopupCompletion)
            # completion list will be hidden now; we will show it again after a delay
            QTimer.singleShot(100, self.callPopup)
        else:
            self.completer().setCompletionMode(QCompleter.PopupCompletion)

    def callPopup(self):
        self.completer().setCompletionPrefix("")
        self.completer().complete()
