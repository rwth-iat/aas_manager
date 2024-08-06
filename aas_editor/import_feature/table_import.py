#  Copyright (C) 2022  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
import copy
import traceback
from typing import Any

from PyQt6.QtCore import QModelIndex, Qt, QPersistentModelIndex
from basyx.aas.model import Referable

from aas_editor.import_feature.import_settings import MAPPING_ATTR
from aas_editor.import_feature.item_import_treeview import ImportTreeViewItem
from aas_editor.import_feature.import_util_classes import PreObjectImport
from aas_editor.models import PacksTable, PackTreeViewItem, SetDataItem
from aas_editor.settings import ATTRIBUTE_COLUMN, OBJECT_ROLE, COLUMN_NAME_ROLE, EXTENDED_COLUMNS_IN_PACK_TABLE, \
    ADD_ITEM_ROLE, CLEAR_ROW_ROLE, DATA_CHANGE_FAILED_ROLE


class ImportTable(PacksTable):
    itemTyp = ImportTreeViewItem

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if role == Qt.ItemDataRole.EditRole:
            parentObj = super(ImportTable, self).data(index, OBJECT_ROLE)
            if isinstance(parentObj, Referable):
                objVal = super(ImportTable, self).data(index, Qt.ItemDataRole.EditRole)

                if index.column() == ATTRIBUTE_COLUMN:
                    objVal = copy.deepcopy(objVal)  # important to handle NamespaceSets in basyx-python
                    preObj = PreObjectImport.fromObject(objVal)
                    mapping = getattr(objVal, MAPPING_ATTR, {})
                    preObj.setMapping(mapping)
                    return preObj
                elif index.data(COLUMN_NAME_ROLE) in EXTENDED_COLUMNS_IN_PACK_TABLE:
                    preObj = PreObjectImport.fromObject(objVal)
                    attr = index.data(COLUMN_NAME_ROLE)
                    mapping = getattr(parentObj, MAPPING_ATTR, {})
                    if attr in mapping:
                        preObj.setMapping(mapping[attr])
                    return preObj
        return super(ImportTable, self).data(index, role)

    def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        try:
            preObject = None
            if isinstance(value, PreObjectImport):
                preObject = value
                value = preObject.initWithExampleRowImport()

            result = super(ImportTable, self).setData(index, value, role)

            if preObject and result and role in (Qt.ItemDataRole.EditRole, ADD_ITEM_ROLE):
                if isinstance(value, Referable):
                    setattr(value, MAPPING_ATTR, preObject.getMapping())
                elif isinstance(self.data(index, OBJECT_ROLE), Referable):
                    parentObj = index.data(OBJECT_ROLE)
                    attrName = index.data(COLUMN_NAME_ROLE)
                    mapping = getattr(parentObj, MAPPING_ATTR, {})
                    mapping[attrName] = preObject.getMapping()

            if preObject and result:
                if role == Qt.ItemDataRole.EditRole:
                    self.undo.pop()
                    self.undo.append(SetDataItem(index=QPersistentModelIndex(index), value=preObject, role=role))
                elif role == CLEAR_ROW_ROLE:
                    self.undo.pop()
                    self.undo.append(SetDataItem(index=QPersistentModelIndex(index), value=preObject, role=ADD_ITEM_ROLE))

            return result
        except Exception as e:
            tb = traceback.format_exc()
            self.lastErrorMsg = f"Error occurred: {e}\n\n{tb}"
            self.dataChanged.emit(index, index, [DATA_CHANGE_FAILED_ROLE])
            return False
