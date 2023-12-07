#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/

from typing import Any, Union, Iterable

from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QFont

from aas_editor.models import StandardTable, PackTreeViewItem
from aas_editor.package import Package
from aas_editor.settings.app_settings import PACKAGE_ROLE, DEFAULT_FONT, OPENED_PACKS_ROLE, OPENED_FILES_ROLE, \
    DEFAULT_COLUMNS_IN_PACKS_TABLE, OBJECT_ROLE, COLUMN_NAME_ROLE, NAME_ROLE
from aas_editor.utils.util_classes import ClassesInfo


class PacksTable(StandardTable):
    itemTyp = PackTreeViewItem
    currFont = QFont(DEFAULT_FONT)

    def openedPacks(self):
        packs = set()
        for i in range(self.rowCount()):
            item = self.index(row=i)
            pack: Package = item.data(PACKAGE_ROLE)
            if pack:
                try:
                    packs.add(pack)
                except AttributeError:
                    continue
        return packs

    def openedFiles(self):
        files = set([pack.file for pack in self.openedPacks()])
        return files

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if role == Qt.ForegroundRole:
            return self._getFgColor(index)
        elif role == OPENED_PACKS_ROLE:
            return self.openedPacks()
        elif role == OPENED_FILES_ROLE:
            return self.openedFiles()
        else:
            return super(PacksTable, self).data(index, role)

    def editItem(self, index: QModelIndex, value):
        value = None if str(value) == "None" else value
        if index.data(COLUMN_NAME_ROLE) not in DEFAULT_COLUMNS_IN_PACKS_TABLE:
            parentObj = index.data(OBJECT_ROLE)
            objName = index.data(COLUMN_NAME_ROLE)
            oldValue = getattr(parentObj, objName)
            setattr(parentObj, objName, value)
            return value, oldValue
        else:
            return super().editItem(index, value)

    def update(self, index: QModelIndex):
        self.dataChanged.emit(index.siblingAtColumn(0),
                              index.siblingAtColumn(self.columnCount()))
        return True

    def _addItemObjToParentObj(self, obj: Union[Package, 'SubmodelElement', Iterable], parent: QModelIndex):
        parentObj = parent.data(OBJECT_ROLE)
        parentObjCls = type(parentObj)
        parentName = parent.data(NAME_ROLE)
        if isinstance(obj, Package):
            return
        elif parentName in Package.addableAttrs():
            package: Package = parent.data(PACKAGE_ROLE)
            package.add(obj)
        elif ClassesInfo.changedParentObject(parentObjCls): #FIXME: Refactor
            parentObj = getattr(parentObj, ClassesInfo.changedParentObject(parentObjCls))
            parentObj.add(obj)
        else:
            return super()._addItemObjToParentObj(obj, parentObj)

    def _getKwargsForItemInit(self, obj: Union[Package, 'SubmodelElement', Iterable], parent):
        kwargs = super()._getKwargsForItemInit(obj, parent)
        if isinstance(obj, Package):
            kwargs["parent"] = self._rootItem
            kwargs["new"] = False
        return kwargs
