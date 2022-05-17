#  Copyright (C) 2022  Igor Garmaev, garmaev@gmx.net
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
import json
import traceback

from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QMessageBox, QDialog
from basyx.aas.model import AASReference

from aas_editor import dialogs
from aas_editor.import_feature.preobjectAdvanced import PreObjectImport
from aas_editor.import_feature.import_settings import PREOBJECT_ATTR
from aas_editor.package import Package
from aas_editor.settings.app_settings import ADD_ITEM_ROLE, COLUMN_NAME_ROLE, OBJECT_ROLE, PACKAGE_ROLE
from aas_editor.utils.util_classes import DictItem, PreObject
from aas_editor.utils.util_type import isSimpleIterable, getAttrTypeHint, issubtype, isoftype, getTypeName
from aas_editor.widgets import PackTreeView


class ImportTreeView(PackTreeView):
#    def onEditCreate(self, objVal=None, index=QModelIndex()):
#    def updateActions(self, index: QModelIndex):
#    def onAddAct(self, objVal=None, parent: QModelIndex = None):

    def addItemWithDialog(self, parent: QModelIndex, objTypeHint, objVal=None,
                          title="", rmDefParams=False):
        try:
            dialog = dialogs.AddObjDialog(objTypeHint, self, rmDefParams=rmDefParams, objVal=objVal, title=title)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return False

        result = False
        while not result and dialog.exec_() == QDialog.Accepted:
            try:
                preobj = dialog.getPreObj()
                importPreObj = PreObjectImport.fromPreObject(preobj)
                obj = importPreObj.initWithImport()
                setattr(obj, PREOBJECT_ATTR, importPreObj)
            except Exception as e:
                tb = traceback.format_exc()
                err_msg = f"{e}\n\n{tb}".replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")
                QMessageBox.critical(self, "Error", err_msg)
                continue

            if isinstance(obj, dict):
                for key, value in obj.items():
                    result = self.model().setData(parent, DictItem(key, value), ADD_ITEM_ROLE)
            elif isSimpleIterable(obj):
                for i in obj:
                    result = self.model().setData(parent, i, ADD_ITEM_ROLE)
            else:
                result = self.model().setData(parent, obj, ADD_ITEM_ROLE)
        if dialog.result() == QDialog.Rejected:
            print("Item adding cancelled")
        dialog.deleteLater()
        self.setFocus()
        return result

    def onEditCreate(self, objVal=None, index=QModelIndex()):
        """
        :param objVal: value to set in dialog input widgets
        :raise KeyError if no typehint found and no objVal was given
        """
        if not index.isValid():
            index = self.currentIndex()
        if index.isValid():
            objVal = objVal if objVal else index.data(Qt.EditRole)
            if hasattr(objVal, PREOBJECT_ATTR):
                objVal = getattr(objVal, PREOBJECT_ATTR)
            attribute = index.data(COLUMN_NAME_ROLE)
            parentObj = index.data(OBJECT_ROLE)
            try:
                attrTypeHint = getAttrTypeHint(type(parentObj), attribute)
            except KeyError as e:
                if objVal:
                    if isoftype(objVal, PreObject):
                        attrTypeHint = objVal.objType
                    else:
                        attrTypeHint = type(objVal)
                else:
                    raise KeyError("No typehint found for the given item", attribute)
            self.replItemWithDialog(index, attrTypeHint, title=f"Edit/Create {attribute}", objVal=objVal)

    def savePack(self, pack: Package = None, file: str = None) -> bool:
        pack = self.currentIndex().data(PACKAGE_ROLE) if pack is None else pack
        try:
            pack.write(file)
            self.updateRecentFiles(pack.file.absolute().as_posix())

            res = dict()
            for obj in pack.objStore:
                reference = repr(AASReference.from_referable(obj))
                if hasattr(obj, PREOBJECT_ATTR):
                    preObj = getattr(obj, PREOBJECT_ATTR)
                    mappings = preObj.mappingList(reference, "")
                    res[reference] = mappings
            for refObjMap in res:
                for attr in res[refObjMap]:
                    attr["value_type"] = getTypeName(attr["value_type"])
            with open('writed_json.json', 'w') as jsonFile:
                json.dump(res, jsonFile)
                jsonFile.close()
            return True
        except (TypeError, ValueError, KeyError) as e:
            QMessageBox.critical(self, "Error", f"Package couldn't be saved: {file}: {e}")
        except AttributeError as e:
            QMessageBox.critical(self, "Error", f"No chosen package to save: {e}")
        return False

    def saveMapping(self, pack: Package = None, file: str = None) -> bool:
        pack = self.currentIndex().data(PACKAGE_ROLE) if pack is None else pack
        try:
            res = dict()
            for obj in pack.objStore:
                reference = repr(AASReference.from_referable(obj))
                if hasattr(obj, PREOBJECT_ATTR):
                    preObj = getattr(obj, PREOBJECT_ATTR)
                    mappings = preObj.mappingList(reference, "")
                    res[reference] = mappings
            for refObjMap in res:
                for attr in res[refObjMap]:
                    if isinstance(attr, dict):
                        attr["value_type"] = getTypeName(attr["value_type"])
                    else:
                        for i in attr:
                            i["value_type"] = getTypeName(i["value_type"])
            with open(file, 'w') as jsonFile:
                json.dump(res, jsonFile)
                jsonFile.close()
            return True
        #except (TypeError, ValueError, KeyError) as e:
        #    QMessageBox.critical(self, "Error", f"Package couldn't be saved: {file}: {e}")
        except AttributeError as e:
            QMessageBox.critical(self, "Error", f"No chosen package to save: {e}")
        return False
