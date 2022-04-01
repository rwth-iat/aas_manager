#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
from typing import AbstractSet

from PyQt5 import QtWidgets
from PyQt5.QtGui import QPainter, QBrush, QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import QWidget, QStyledItemDelegate, QStyleOptionViewItem, QStyle, \
    QCompleter, QCheckBox
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QModelIndex

from basyx.aas.model.aas import *
from basyx.aas.model.base import *
from basyx.aas.model.concept import *
from basyx.aas.model.submodel import *

from aas_editor.settings import DEFAULT_COMPLETIONS
from aas_editor.utils.util import inheritors
from aas_editor.utils.util_classes import DictItem
from aas_editor.utils.util_type import issubtype, getTypeName, isoftype
from aas_editor.widgets import CompleterComboBox
from aas_editor.widgets.combobox import ComboBox
from aas_editor.widgets.dictItemEdit import DictItemEdit
from aas_editor.widgets.lineEdit import LineEdit


class ColorDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.indexColors: Dict[QModelIndex, QBrush] = {}
        self.hoverIndex = QModelIndex()

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        opt = QStyleOptionViewItem(option)
        # paint row of the tree with MouseOver style if one cell of the row is chosen
        if not opt.state & QStyle.State_HasFocus:
            view = opt.styleObject
            hoverIndex: QModelIndex = view.currentIndex()
            if not opt.state & QStyle.State_MouseOver and index.siblingAtColumn(0) == hoverIndex.siblingAtColumn(0):
                opt.state |= QStyle.State_MouseOver
                model = view.model()
                model.dataChanged.emit(index, index)

        if index.isValid() and index in self.indexColors:
            self.initStyleOption(opt, index)
            opt.backgroundBrush = self.indexColors[index]
            widget = opt.widget
            style = widget.style()
            style.drawControl(QStyle.CE_ItemViewItem, opt, painter, widget)
        else:
            super(ColorDelegate, self).paint(painter, opt, index)

    def setBgColor(self, index: QModelIndex, val: QBrush):
        self.indexColors[index] = val

    def bgColor(self, index: QModelIndex):
        return self.indexColors[index]

    def removeBgColor(self, index: QModelIndex):
        self.indexColors.pop(index)

    def clearBgColors(self):
        self.indexColors.clear()


class EditDelegate(ColorDelegate):
    # FIXME check if other types are also editable
    editableTypesInTable = (bool, int, float, str, Enum, Type, DictItem, bytes, type(None), dict, list, AbstractSet)

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
                widget = ComboBox(parent)
            else:
                widget = CompleterComboBox(parent)
            widget.setAutoFillBackground(True)
        elif issubtype(objType, DictItem):
            widget = DictItemEdit(parent)
        else:
            return super().createEditor(parent, option, index)
        return widget

    def setEditorData(self, editor: QWidget, index: QtCore.QModelIndex) -> None:
        if isinstance(index.data(Qt.EditRole), Enum):
            currItem = index.data(Qt.EditRole)
            items = [member for member in type(currItem)]
            for item in items:
                editor.addItem(item.name, item)
            editor.model().sort(0, Qt.AscendingOrder)
            editor.setCurrentText(currItem.name)
        elif isinstance(index.data(Qt.EditRole), DictItem):
            currItem = index.data(Qt.EditRole)
            editor.setCurrentData(currItem)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor: QWidget, model: QtCore.QAbstractItemModel,
                     index: QtCore.QModelIndex) -> None:
        if isoftype(index.data(Qt.EditRole), (Enum, DictItem)):
            obj = editor.currentData()
            model.setData(index, obj, Qt.EditRole)
        else:
            super().setModelData(editor, model, index)

    def updateEditorGeometry(self, editor: QWidget, option: 'QStyleOptionViewItem',
                             index: QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)
