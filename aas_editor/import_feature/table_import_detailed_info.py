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

from typing import Any, List

from PyQt5.QtCore import QModelIndex, QPersistentModelIndex, Qt
from PyQt5.QtGui import QFont
from basyx.aas.model import Referable

from aas_editor.import_feature.import_settings import MAPPING_ATTR
from aas_editor.import_feature.preobjectAdvanced import PreObjectImport
from aas_editor.models import DetailedInfoItem, DetailedInfoTable, SetDataItem
from aas_editor.settings import EXTENDED_COLUMNS_IN_PACK_TABLE
from aas_editor.settings.app_settings import PACKAGE_ROLE, NAME_ROLE, OBJECT_ROLE, DEFAULT_COLUMNS_IN_DETAILED_INFO, \
    PACK_ITEM_ROLE, DEFAULT_FONT, COLUMN_NAME_ROLE, ATTRIBUTE_COLUMN, ADD_ITEM_ROLE, CLEAR_ROW_ROLE, PARENT_OBJ_ROLE

MAPPING_COLUMN_NAME = "mapping"


class DetailedInfoImportTable(DetailedInfoTable):
    currFont = QFont(DEFAULT_FONT)

    def __init__(self, packItem: QModelIndex):
        self.packItem = QPersistentModelIndex(packItem)
        self.mainObj = packItem.data(OBJECT_ROLE)
        self.package = packItem.data(PACKAGE_ROLE)
        root = DetailedInfoItem(self.mainObj, name=packItem.data(NAME_ROLE),
                                package=self.package, new=False)
        columns = (*DEFAULT_COLUMNS_IN_DETAILED_INFO, MAPPING_COLUMN_NAME)
        super(DetailedInfoTable, self).__init__(columns, root)

    def getChildPath(self, index) -> List[str]:
        objPath = []
        curObj = None
        curIndex = index
        while self.mainObj is not curObj:
            curName: str = self.data(curIndex, NAME_ROLE)
            if curName.split(" ")[-1].isdecimal():
                objPath.insert(0, curName.split(" ")[-1])
            else:
                objPath.insert(0, curName)
            curObj = curIndex.data(PARENT_OBJ_ROLE)
            curIndex = curIndex.parent()
        return objPath

    def getMapping4ChildPath(self, path: List[str]):
        mapping = getattr(self.mainObj, MAPPING_ATTR, {})
        for attrName in path:
            if attrName in mapping:
                if isinstance(mapping[attrName], dict):
                    mapping = mapping[attrName]
                else:
                    return mapping[attrName]
            else:
                mapping = {}
        return mapping

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if role == Qt.DisplayRole and super(DetailedInfoImportTable, self).data(index, COLUMN_NAME_ROLE) == MAPPING_COLUMN_NAME:
            objPath = self.getChildPath(index)
            mapping = self.getMapping4ChildPath(objPath)
            return mapping
        elif role == Qt.EditRole and isinstance(self.mainObj, Referable):
            objVal = super(DetailedInfoImportTable, self).data(index, OBJECT_ROLE)
            preObj = PreObjectImport.fromObject(objVal)
            objPath = self.getChildPath(index)
            mapping = self.getMapping4ChildPath(objPath)
            preObj.setMapping(mapping)
            return preObj
        return super(DetailedInfoTable, self).data(index, role)

    def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        preObject = None
        if isinstance(value, PreObjectImport):
            preObject = value
            value = preObject.initWithImport()

        result = super(DetailedInfoTable, self).setData(index, value, role)

        if preObject and result and role in (Qt.EditRole, ADD_ITEM_ROLE) and isinstance(self.mainObj, Referable):
            mapping = getattr(self.mainObj, MAPPING_ATTR)
            childPath = self.getChildPath(index)
            for attr in childPath:
                if attr not in mapping:
                    mapping[attr] = {}
                mapping = mapping[attr]
            mapping.update(preObject.getMapping())

        if preObject and result:
            if role == Qt.EditRole:
                self.undo.pop()
                self.undo.append(SetDataItem(index=QPersistentModelIndex(index), value=preObject, role=role))
            elif role == CLEAR_ROW_ROLE:
                self.undo.pop()
                self.undo.append(SetDataItem(index=QPersistentModelIndex(index), value=preObject, role=ADD_ITEM_ROLE))

        return result
