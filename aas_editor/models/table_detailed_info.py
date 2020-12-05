from typing import Any

from PyQt5.QtCore import QModelIndex, QVariant, Qt, QPersistentModelIndex
from PyQt5.QtGui import QFont, QBrush

from aas_editor.models import DetailedInfoItem, StandardTable
from aas_editor.settings import PACKAGE_ROLE, NAME_ROLE, OBJECT_ROLE, \
    COLUMNS_IN_DETAILED_INFO, ATTRIBUTE_COLUMN, VALUE_COLUMN, PACK_ITEM_ROLE, LIGHT_BLUE, \
    LINK_BLUE, CHANGED_BLUE, NEW_GREEN, DEFAULT_FONT, LINKED_ITEM_ROLE, IS_LINK_ROLE


class DetailedInfoTable(StandardTable):
    defaultFont = QFont(DEFAULT_FONT)

    def __init__(self, packItem: QModelIndex):
        self.packItem = QPersistentModelIndex(packItem)
        self.mainObj = packItem.data(OBJECT_ROLE)
        self.package = packItem.data(PACKAGE_ROLE)
        root = DetailedInfoItem(self.mainObj, name=packItem.data(NAME_ROLE),
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
        if role == LINKED_ITEM_ROLE:
            return self.getLinkedItem(index)
        else:
            return super(DetailedInfoTable, self).data(index, role)

    def _getBgColor(self, index: QModelIndex):
        bg = self.objByIndex(index).data(Qt.BackgroundRole)
        if isinstance(bg, QBrush) and bg.color().alpha():
            return bg.color()

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
            if index.data(IS_LINK_ROLE):
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
            if index.data(IS_LINK_ROLE):
                font.setUnderline(True)

        return font

    def getLinkedItem(self, index: QModelIndex) -> QModelIndex:
        if not index.data(IS_LINK_ROLE):
            return QModelIndex()
        try:
            reference = self.data(index, OBJECT_ROLE)
            objStore = self.data(index, PACKAGE_ROLE).objStore
            obj = reference.resolve(objStore)
            linkedPackItem, = self.data(index, PACK_ITEM_ROLE).model().match(QModelIndex(), OBJECT_ROLE, obj, hits=1)
            return linkedPackItem
        except AttributeError:
            return QModelIndex()
