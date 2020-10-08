import typing

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QStyledItemDelegate
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.Qt import QStandardItemModel, QStandardItem

from enum import Enum
from aas.model.aas import *
from aas.model.base import *
from aas.model.concept import *
from aas.model.submodel import *

from .models import NAME_ROLE

STR_ATTRS = [
    "id_short",
    "category",
    "version",
    "revision",
]

STR_DICT = [
    "description"
]

class QComboBoxEnumDelegate(QStyledItemDelegate):
    def __init__(self):
        super().__init__()

    def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QWidget:
        if isinstance(index.data(Qt.EditRole), Enum):
            editor = QtWidgets.QComboBox(parent)
            editor.setAutoFillBackground(True)
        elif index.data(NAME_ROLE) in STR_ATTRS:
            editor = super().createEditor(parent, option, index)
        else:
            editor = super().createEditor(parent, option, index)
        return editor

    def setEditorData(self, editor: QWidget, index: QtCore.QModelIndex) -> None:
        if isinstance(index.model().data(index, Qt.EditRole), Enum):
            currItem = index.model().data(index, Qt.EditRole)
            items = [member for member in type(currItem)]
            for item in items:
                editor.addItem(item.name, item)
            editor.setCurrentText(currItem.name)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor: QWidget, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex) -> None:
        if isinstance(index.model().data(index, Qt.EditRole), Enum):
            obj = editor.currentData()
            model.setData(index, obj, Qt.EditRole)
        else:
            super().setModelData(editor, model, index)

    def updateEditorGeometry(self, editor: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)

    # def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> None:
    #     pass