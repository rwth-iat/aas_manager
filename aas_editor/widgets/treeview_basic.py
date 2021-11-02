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

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtGui import QMouseEvent, QPaintEvent, QPainter, QWheelEvent
from PyQt5.QtWidgets import QTreeView

from aas_editor.models.search_proxy_model import SearchProxyModel
from aas_editor.settings.app_settings import *

EMPTY_VIEW_MSG = "There are no elements in this view"
EMPTY_VIEW_ICON = None


class BasicTreeView(QTreeView):
    wheelClicked = pyqtSignal(['QModelIndex'])
    ctrlWheelScrolled = pyqtSignal(int)
    modelChanged = pyqtSignal(['QAbstractItemModel'])

    def __init__(self, parent=None, *, emptyViewMsg=EMPTY_VIEW_MSG, emptyViewIcon=EMPTY_VIEW_ICON):
        super(BasicTreeView, self).__init__(parent)
        self.emptyViewMsg = emptyViewMsg
        self.emptyViewIcon = emptyViewIcon

    def setModel(self, model: QtCore.QAbstractItemModel) -> None:
        super(BasicTreeView, self).setModel(model)
        self.modelChanged.emit(model)

    def setModelWithProxy(self, model: QtCore.QAbstractItemModel) -> None:
        # proxy model will always be used by setting new models
        proxyModel = SearchProxyModel()
        proxyModel.setSourceModel(model)
        self.setModel(proxyModel)

    def sourceModel(self):
        try:
            return self.model().sourceModel()
        except AttributeError:
            return self.model()

    def collapse(self, index: QtCore.QModelIndex) -> None:
        newIndex = index.siblingAtColumn(0)
        super(BasicTreeView, self).collapse(newIndex)

    def expand(self, index: QtCore.QModelIndex) -> None:
        newIndex = index.siblingAtColumn(0)
        super(BasicTreeView, self).expand(newIndex)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MiddleButton:
            self.wheelClicked.emit(self.indexAt(event.pos()))
        else:
            super(BasicTreeView, self).mouseReleaseEvent(event)

    def wheelEvent(self, a0: QWheelEvent) -> None:
        if a0.modifiers() & Qt.ControlModifier:
            # ctrl press + scroll
            delta = a0.angleDelta().y()
            self.ctrlWheelScrolled.emit(delta)
        else:
            super(BasicTreeView, self).wheelEvent(a0)

    def paintEvent(self, e: QPaintEvent) -> None:
        if (self.model() and self.model().rowCount()) \
                or not (self.emptyViewMsg or self.emptyViewIcon):
            super(BasicTreeView, self).paintEvent(e)
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
