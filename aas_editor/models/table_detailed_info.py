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

from PyQt6.QtCore import QModelIndex, QPersistentModelIndex, Qt
from PyQt6.QtGui import QFont

from aas_editor.models import DetailedInfoItem, StandardTable
from aas_editor.package import Package
from aas_editor.settings.app_settings import PACKAGE_ROLE, NAME_ROLE, OBJECT_ROLE, DEFAULT_COLUMNS_IN_DETAILED_INFO,\
    PACK_ITEM_ROLE, DEFAULT_FONT, PARENT_OBJ_ROLE


class DetailedInfoTable(StandardTable):
    itemTyp = DetailedInfoItem
    currFont = QFont(DEFAULT_FONT)

    def __init__(self, packItem: QModelIndex):
        self.packItem = QPersistentModelIndex(packItem)
        self.mainObj = packItem.data(OBJECT_ROLE)
        self.package = packItem.data(PACKAGE_ROLE)
        root = DetailedInfoItem(self.mainObj, name=packItem.data(NAME_ROLE),
                                package=self.package, new=False)
        super(DetailedInfoTable, self).__init__(DEFAULT_COLUMNS_IN_DETAILED_INFO, root)

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if role == PACK_ITEM_ROLE:
            return QModelIndex(self.packItem)
        else:
            return super(DetailedInfoTable, self).data(index, role)

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        flags = super().flags(index)
        # Package attributes are read-only info (file, stores, app settings);
        # neither the cell editor nor the edit dialog can handle them
        if isinstance(index.data(PARENT_OBJ_ROLE), Package):
            flags &= ~Qt.ItemFlag.ItemIsEditable
        return flags
