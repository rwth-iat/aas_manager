from typing import Any

from PyQt5.QtCore import pyqtSignal, QModelIndex, QVariant, Qt, QPersistentModelIndex, QSize
from PyQt5.QtGui import QColor, QFont

from aas_editor.models import Package, DetailedInfoItem, StandardTable
from aas_editor.settings import PACKAGE_ROLE, NAME_ROLE, OBJECT_ROLE, COLUMNS_IN_DETAILED_INFO, \
    ATTRIBUTE_COLUMN, VALUE_COLUMN, PACK_ITEM_ROLE, LIGHT_BLUE, LINK_BLUE, CHANGED_BLUE, NEW_GREEN, \
    DEFAULT_FONT


class DetailedInfoTable(StandardTable):
    defaultFont = QFont(DEFAULT_FONT)

    def __init__(self, packItem: QModelIndex):
        self.packItem = QPersistentModelIndex(packItem)
        self.mainObj = packItem.data(OBJECT_ROLE)
        self.package = packItem.data(PACKAGE_ROLE)
        root = DetailedInfoItem(self.mainObj, packItem.data(NAME_ROLE),
                                package=self.package, new=False)
        super(DetailedInfoTable, self).__init__(COLUMNS_IN_DETAILED_INFO, root)

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if role == Qt.BackgroundRole:
            return self._getBgColor(index)
        if role == Qt.ForegroundRole:
            return self._getFgColor(index)
        if role == Qt.FontRole:
            return self._getFont(index)
        if role == PACK_ITEM_ROLE:
            return QModelIndex(self.packItem)
        else:
            return super(DetailedInfoTable, self).data(index, role)

    def _getBgColor(self, index: QModelIndex):
        color = LIGHT_BLUE
        if index.parent().isValid():
            if index.row() == 0:
                color.setAlpha(260 - index.parent().data(Qt.BackgroundRole).alpha())
            else:
                color.setAlpha(
                    260 - index.siblingAtRow(index.row() - 1).data(Qt.BackgroundRole).alpha())
        else:
            if index.row() % 2:
                color.setAlpha(150)
            else:
                color.setAlpha(110)
        return color

    def _getFgColor(self, index: QModelIndex):
        if index.column() == VALUE_COLUMN:
            if self.objByIndex(index).isLink:
                return LINK_BLUE
        elif index.column() == ATTRIBUTE_COLUMN:
            if self.objByIndex(index).new:
                color = NEW_GREEN
                return color
            elif self.objByIndex(index).changed:
                color = CHANGED_BLUE
                return color
            return QVariant()
        return QVariant()

    def _getFont(self, index: QModelIndex):
        font = QFont(self.defaultFont)
        if index.column() == ATTRIBUTE_COLUMN:
            if not isinstance(index.parent().data(OBJECT_ROLE), dict):
                font.setBold(True)
        elif index.column() == VALUE_COLUMN:
            if self.objByIndex(index).isLink:
                font.setUnderline(True)

        return font
