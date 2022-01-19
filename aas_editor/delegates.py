#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/

from PyQt5 import QtWidgets
from PyQt5.QtGui import QPainter, QBrush, QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import QWidget, QStyledItemDelegate, QStyleOptionViewItem, QStyle, \
    QCompleter, QCheckBox, QComboBox
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QModelIndex

from enum import Enum
from aas.model.aas import *
from aas.model.base import *
from aas.model.concept import *
from aas.model.submodel import *

from aas_editor.settings import DEFAULT_COMPLETIONS
from aas_editor.utils.util import inheritors
from aas_editor.utils.util_type import issubtype, getTypeName
from aas_editor.widgets import CompleterComboBox
from aas_editor.widgets.lineEdit import LineEdit


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
    def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem',
                     index: QtCore.QModelIndex) -> QWidget:
        objType = type(index.data(Qt.EditRole))
        attr = index.data(Qt.DisplayRole)
        if issubtype(objType, bool):
            widget = QCheckBox(parent)
        elif issubtype(objType, str):
            widget = LineEdit(parent)
            completions = DEFAULT_COMPLETIONS.get(objType, {}).get(attr, [])
            if completions:
                completer = QCompleter(parent, completions=completions)
                widget.setCompleter(completer)
        elif issubtype(objType, int):
            widget = LineEdit(parent)
            widget.setValidator(QIntValidator())
        elif issubtype(objType, float):
            widget = LineEdit(parent)
            widget.setValidator(QDoubleValidator())
        elif issubtype(objType, (Enum, Type)):
            if issubtype(objType, Enum):
                # add enum types to types
                types = [member for member in objType]
            else:  # Type
                union = objType.__args__[0]
                if type(union) == TypeVar:
                    # add Type inheritors to types
                    baseType = union.__bound__
                    types = inheritors(baseType)
                else:
                    # add Union Type attrs to types
                    types = union.__args__

            if len(types) <= 6:
                widget = QComboBox(parent)
            else:
                widget = CompleterComboBox(parent)

            for typ in types:
                widget.addItem(getTypeName(typ), typ)
            widget.model().sort(0, Qt.AscendingOrder)
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
