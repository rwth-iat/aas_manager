from PyQt5 import QtWidgets
from PyQt5.QtGui import QPainter, QBrush
from PyQt5.QtWidgets import QWidget, QStyledItemDelegate, QStyleOptionViewItem, QStyle
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QModelIndex

from enum import Enum
from aas.model.aas import *
from aas.model.base import *
from aas.model.concept import *
from aas.model.submodel import *


class ColorDelegate(QStyledItemDelegate):
    def __init__(self):
        super().__init__()
        self.indexColors: Dict[QModelIndex, QBrush] = {}

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        if index.isValid() and index in self.indexColors:
            self.initStyleOption(option, index)
            option.backgroundBrush = self.indexColors[index]
            widget = option.widget
            style = widget.style()
            style.drawControl(QStyle.CE_ItemViewItem, option, painter, widget)
        else:
            super(ColorDelegate, self).paint(painter, option, index)

    def setBgColor(self, index: QModelIndex, val: QBrush):
        self.indexColors[index] = val

    def bgColor(self, index: QModelIndex):
        return self.indexColors[index]

    def removeBgColor(self, index: QModelIndex):
        self.indexColors.pop(index)

    def clearBgColors(self):
        self.indexColors.clear()


class EditDelegate(ColorDelegate):
    def __init__(self):
        super().__init__()

    def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem',
                     index: QtCore.QModelIndex) -> QWidget:
        if isinstance(index.data(Qt.EditRole), Enum):
            editor = QtWidgets.QComboBox(parent)
            editor.setAutoFillBackground(True)
        else:
            editor = super().createEditor(parent, option, index)
        return editor

    def setEditorData(self, editor: QWidget, index: QtCore.QModelIndex) -> None:
        if isinstance(index.data(Qt.EditRole), Enum):
            currItem = index.data(Qt.EditRole)
            items = [member for member in type(currItem)]
            for item in items:
                editor.addItem(item.name, item)
            editor.setCurrentText(currItem.name)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor: QWidget, model: QtCore.QAbstractItemModel,
                     index: QtCore.QModelIndex) -> None:
        if isinstance(index.data(Qt.EditRole), Enum):
            obj = editor.currentData()
            model.setData(index, obj, Qt.EditRole)
        else:
            super().setModelData(editor, model, index)

    def updateEditorGeometry(self, editor: QWidget, option: 'QStyleOptionViewItem',
                             index: QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)
