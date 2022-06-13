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
from PyQt5.QtWidgets import QMessageBox, QAction
from basyx.aas import model

from aas_editor import dialogs
from aas_editor.import_feature.preobjectAdvanced import PreObjectImport
from aas_editor.import_feature.import_settings import MAPPING_ATTR
from aas_editor.package import Package
from aas_editor.settings import NEW_PACK_ICON, OPEN_ICON, SC_OPEN, AAS_FILES_FILTER, ALL_FILES_FILTER
from aas_editor.settings.app_settings import PACKAGE_ROLE
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
        return PreObjectImport.fromPreObject(dialog.getPreObj())

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

