#  Copyright (C) 2022  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
import json
import traceback

from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QMessageBox, QDialog, QAction
from basyx.aas import model
from basyx.aas.model import AASReference

from aas_editor import dialogs
from aas_editor.import_feature.preobjectAdvanced import PreObjectImport
from aas_editor.import_feature.import_settings import MAPPING_ATTR
from aas_editor.package import Package
from aas_editor.settings import NEW_PACK_ICON, OPEN_ICON, SC_OPEN, AAS_FILES_FILTER, ALL_FILES_FILTER
from aas_editor.settings.app_settings import COLUMN_NAME_ROLE, OBJECT_ROLE, PACKAGE_ROLE, \
    DEFAULT_COLUMNS_IN_PACKS_TABLE, ATTRIBUTE_COLUMN
from aas_editor.utils.util_type import isIterable
from aas_editor.widgets import PackTreeView
import basyx
from basyx.aas.model import *


class ImportTreeView(PackTreeView):
#    def updateActions(self, index: QModelIndex):
#    def onAddAct(self, objVal=None, parent: QModelIndex = None):
#    def onEdit

    def __init__(self, parent=None, *, importManageWidget):
        super(ImportTreeView, self).__init__(parent)
        self.importManageWidget = importManageWidget

    def initActions(self):
        super(ImportTreeView, self).initActions()
        aasx_filter = f"{AAS_FILES_FILTER};;{ALL_FILES_FILTER}"
        self.newPackAct = QAction(NEW_PACK_ICON, "&New AASX Import Mapping file", self,
                                  statusTip="Create new AAS file for import mapping",
                                  triggered=lambda: self.newPackWithDialog(filter=aasx_filter),
                                  enabled=True)

        self.openPackAct = QAction(OPEN_ICON, "&Open AASX/AASX Import Mapping file", self,
                                   shortcut=SC_OPEN,
                                   statusTip="Open AASX file or AASX import mapping file",
                                   triggered=lambda: self.openPackWithDialog(filter=aasx_filter),
                                   enabled=True)

        self.saveAsAct = QAction("Save As...", self,
                                 statusTip="Save current AASX Import Mapping file as..",
                                 triggered=lambda: self.savePackAsWithDialog(filter=aasx_filter),
                                 enabled=False)

    def _getObjFromDialog(self, dialog):
        importPreObj = PreObjectImport.fromPreObject(dialog.getPreObj())
        obj = importPreObj.initWithImport()
        self.lastMapping = importPreObj.getMapping()
        return obj

    def _setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        result = super(ImportTreeView, self)._setData(index, value, role)
        if isinstance(value, Referable):
            setattr(value, MAPPING_ATTR, self.lastMapping)
            self.lastMapping = None
        else:
            parentObj = self.model().data(index, OBJECT_ROLE)
            attrName = self.model().data(index, COLUMN_NAME_ROLE)
            if isinstance(parentObj, Referable):
                mapping = getattr(parentObj, MAPPING_ATTR, {})
                mapping[attrName] = self.lastMapping
        self.lastMapping = None
        return result

    def onEditCreate(self, objVal=None, index=QModelIndex()) -> bool:
        """
        :param objVal: value to set in dialog input widgets
        :raise KeyError if no typehint found and no objVal was given
        """
        if not index.isValid():
            index = self.currentIndex()
        if index.isValid():
            if index.column() == ATTRIBUTE_COLUMN:
                objVal = objVal if objVal else index.data(Qt.EditRole)
                preObj = PreObjectImport.fromObject(objVal)
                mapping = getattr(objVal, MAPPING_ATTR, {})
                preObj.setMapping(mapping)
                return self._onEditCreate(preObj, index)
            elif index.data(COLUMN_NAME_ROLE) not in DEFAULT_COLUMNS_IN_PACKS_TABLE:
                objVal = objVal if objVal else index.data(Qt.EditRole)
                preObj = PreObjectImport.fromObject(objVal)
                parentObj = index.data(OBJECT_ROLE)
                attr = index.data(COLUMN_NAME_ROLE)
                mapping = getattr(parentObj, MAPPING_ATTR, {})
                if attr in mapping:
                    preObj.setMapping(mapping[attr])
                return self._onEditCreate(preObj, index)

    def saveMapping(self, pack: Package = None, file: str = None) -> bool:
        pack = self.currentIndex().data(PACKAGE_ROLE) if pack is None else pack
        try:
            mapDict = dict()
            for obj in pack.objStore:
                self._saveMapping(obj, mapDict)
            with open(file, 'w') as jsonFile:
                json.dump(mapDict, jsonFile)
                jsonFile.close()
            return True
        except (TypeError, ValueError, KeyError) as e:
            QMessageBox.critical(self, "Error", f"Package couldn't be saved: {file}: {e}")
        except AttributeError as e:
            QMessageBox.critical(self, "Error", f"No chosen package to save: {e}")
        return False

    def _saveMapping(self, obj, mapDict):
        self._saveMapping4referable(obj, mapDict)
        if isIterable(obj):
            for i in obj:
                self._saveMapping(i, mapDict)

    def _saveMapping4referable(self, obj, mapDict):
        mapping = getattr(obj, MAPPING_ATTR, {})
        if mapping:
            ref = AASReference.from_referable(obj)
            keys = ','.join([f"Key(type_={i.type}, local={i.local}, id_type={i.id_type}, value='{i.value}')" for i in ref.key])
            target_type = repr(ref.type).lstrip("<class '").rstrip("'>")
            mapDict[f"AASReference(target_type={target_type}, key=({keys},))"] = mapping

    def setMapping(self, pack: Package=None, file: str=None) -> bool:
        pack = self.currentIndex().data(PACKAGE_ROLE) if pack is None else pack

        with open(file, 'r') as jsonFile:
            mapDict = json.load(jsonFile)

        for refRepr in mapDict:
            aasref: AASReference = eval(refRepr, {
                "KeyElements": model.KeyElements,
                "KeyType": model.KeyType,
                "Key": Key,
                "AASReference": AASReference,
                "basyx": basyx,
            })
            refObj = aasref.resolve(pack.objStore)
            mapping = mapDict[refRepr]
            setattr(refObj, MAPPING_ATTR, mapping)

