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

from typing import Any

from PyQt5.QtCore import QModelIndex, Qt, QPersistentModelIndex
from PyQt5.QtGui import QFont, QBrush

from aas_editor.models import DetailedInfoItem, StandardTable
from aas_editor.settings.app_settings import PACKAGE_ROLE, NAME_ROLE, OBJECT_ROLE, COLUMNS_IN_DETAILED_INFO,\
    ATTRIBUTE_COLUMN, PACK_ITEM_ROLE, DEFAULT_FONT, LINKED_ITEM_ROLE, IS_LINK_ROLE
from aas_editor.settings import LIGHT_BLUE


class DetailedInfoTable(StandardTable):
    currFont = QFont(DEFAULT_FONT)

    def __init__(self, packItem: QModelIndex):
        self.packItem = QPersistentModelIndex(packItem)
        self.mainObj = packItem.data(OBJECT_ROLE)
        self.package = packItem.data(PACKAGE_ROLE)
        root = DetailedInfoItem(self.mainObj, name=packItem.data(NAME_ROLE),
                                package=self.package, new=False)
        super(DetailedInfoTable, self).__init__(COLUMNS_IN_DETAILED_INFO, root)

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if role == PACK_ITEM_ROLE:
            return QModelIndex(self.packItem)
        if role == LINKED_ITEM_ROLE:
            return self.getLinkedItem(index)
        else:
            return super(DetailedInfoTable, self).data(index, role)

    def _getFont(self, index: QModelIndex):
        font = super(DetailedInfoTable, self)._getFont(index)
        if index.column() == ATTRIBUTE_COLUMN:
            if not isinstance(index.parent().data(OBJECT_ROLE), dict):
                font.setBold(True)
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
