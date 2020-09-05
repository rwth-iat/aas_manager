from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QStyledItemDelegate
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.Qt import QStandardItemModel, QStandardItem

from enum import Enum


class QComboBoxEnumDelegate(QStyledItemDelegate):
    def __init__(self):
        super().__init__()

    def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QWidget:
        if isinstance(index.model().data(index, Qt.EditRole), Enum):
            editor = QtWidgets.QComboBox(parent)
            editor.setAutoFillBackground(True)
        else:
            editor = super().createEditor(parent, option, index)
        return editor

    def setEditorData(self, editor: QWidget, index: QtCore.QModelIndex) -> None:
        if isinstance(index.model().data(index, Qt.EditRole), Enum):
            currItem = index.model().data(index, Qt.EditRole)
            items = [str(member) for member in type(currItem)]
            editor.addItems(items)
            editor.setCurrentText(str(currItem))
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor: QWidget, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex) -> None:
        if isinstance(index.model().data(index, Qt.EditRole), Enum):
            model.setData(index, editor.currentText(), Qt.EditRole)
        else:
            super().setModelData(editor, model, index)

    def updateEditorGeometry(self, editor: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)

    # def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> None:
    #     pass