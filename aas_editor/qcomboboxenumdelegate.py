from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QStyledItemDelegate
from PyQt5 import QtCore
from PyQt5.QtCore import Qt

from enum import Enum
from aas.model.aas import *
from aas.model.base import *
from aas.model.concept import *
from aas.model.submodel import *

from aas_editor.util_classes import DictItem
from .settings import NAME_ROLE, VALUE_COLUMN, ATTRIBUTE_COLUMN

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

    def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem',
                     index: QtCore.QModelIndex) -> QWidget:
        if isinstance(index.data(Qt.EditRole), Enum):
            editor = QtWidgets.QComboBox(parent)
            editor.setAutoFillBackground(True)
        elif isinstance(index.data(Qt.EditRole), DictItem):
            editor = QtWidgets.QLineEdit(parent)
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
        elif isinstance(index.data(Qt.EditRole), DictItem):
            currItem = index.data(Qt.EditRole)
            if index.column() == ATTRIBUTE_COLUMN:
                editor.setText(currItem.key)
            elif index.column() == VALUE_COLUMN:
                editor.setText(currItem.value)
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
