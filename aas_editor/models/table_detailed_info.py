from typing import Any, Iterable

from PyQt5.QtCore import pyqtSignal, QModelIndex, QVariant, Qt
from PyQt5.QtGui import QColor, QFont

from aas_editor.models import Package, COLUMNS_IN_DETAILED_INFO, DetailedInfoItem, StandardTable, \
    VALUE_COLUMN, ATTRIBUTE_COLUMN, OBJECT_ROLE, NAME_ROLE, PACKAGE_ROLE


class DetailedInfoTable(StandardTable):
    def __init__(self, packItem: QModelIndex):
        self.mainObj = packItem.data(OBJECT_ROLE)
        self.package = packItem.data(PACKAGE_ROLE)
        root = DetailedInfoItem(self.mainObj, packItem.data(NAME_ROLE), package=self.package)
        super(DetailedInfoTable, self).__init__(COLUMNS_IN_DETAILED_INFO, root)

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return QVariant()
        if role == Qt.BackgroundRole:
            return self._getBgColor(index)
        if role == Qt.ForegroundRole:
            return self._getFgColor(index)
        if role == Qt.FontRole:
            return self._getFont(index)
        item = self.objByIndex(index)
        return item.data(role, index.column())

    def _getBgColor(self, index: QModelIndex):
        color = QColor(132, 185, 225)
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
                return QColor(26, 13, 171)
        return QVariant()

    def _getFont(self, index: QModelIndex):
        font = QFont()
        if index.column() == ATTRIBUTE_COLUMN:
            if not isinstance(index.parent().data(OBJECT_ROLE), dict):
                font.setBold(True)
            return font
        if index.column() == VALUE_COLUMN:
            if self.objByIndex(index).isLink:
                font.setUnderline(True)
            return font
        return QVariant()

