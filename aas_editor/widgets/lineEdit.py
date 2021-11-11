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
from abc import abstractmethod

from PyQt5.QtCore import pyqtSignal, QRect, QSize
from PyQt5.QtGui import QMouseEvent, QPaintEvent, QPainter, QDropEvent, QDragEnterEvent, QFont
from PyQt5.QtWidgets import QLineEdit, QPlainTextEdit
from PyQt5.QtCore import Qt

from aas_editor.settings import OPEN_DRAG_ICON


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


class DropFilePlainTextEdit(QPlainTextEdit):
    fileDropped = pyqtSignal(str)

    def __init__(self, parent=None, *, emptyViewMsg="Drop AAS files here", emptyViewIcon=OPEN_DRAG_ICON):
        super(QPlainTextEdit, self).__init__(parent)
        self.emptyViewMsg = emptyViewMsg
        self.emptyViewIcon = emptyViewIcon

    def paintEvent(self, e: QPaintEvent) -> None:
        if self.toPlainText() or not (self.emptyViewMsg or self.emptyViewIcon):
            super(DropFilePlainTextEdit, self).paintEvent(e)
        else:
            # If no items draw a text in the center of the viewport.
            position = self.viewport().rect().center()

            if self.emptyViewMsg:
                painter = QPainter(self.viewport())
                textRect = painter.fontMetrics().boundingRect(self.emptyViewMsg)
                textRect.moveCenter(position)
                painter.drawText(textRect, Qt.AlignCenter, self.emptyViewMsg)
                # set position for icon
                position.setY(position.y()+textRect.height()+25)

            if self.emptyViewIcon:
                iconRect = QRect(0, 0, 50, 50)
                iconRect.moveCenter(position)
                painter.drawPixmap(iconRect, self.emptyViewIcon.pixmap(QSize(50, 50)))

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls:
            event.accept()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()

    def dropEvent(self, e: QDropEvent) -> None:
        for url in e.mimeData().urls():
            file = str(url.toLocalFile())
            self.fileDropped.emit(file)
