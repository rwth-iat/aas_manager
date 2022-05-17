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
from types import GeneratorType

from PyQt5.QtCore import QVariant, Qt
from PyQt5.QtWidgets import QMessageBox, QDialog
from basyx.aas.adapter.aasx import DictSupplementaryFileContainer
from basyx.aas.model import AASReference

from aas_editor import dialogs
from aas_editor.import_feature.preobjectAdvanced import PreObjectImport
from aas_editor.import_feature.import_settings import PREOBJECT_ATTR
from aas_editor.models import PackTreeViewItem, StandardItem
from aas_editor.package import Package
from aas_editor.settings import PACKAGE_ROLE, VALUE_COLUMN, ATTRIBUTE_COLUMN, NAME_ROLE
from aas_editor.utils.util_classes import ClassesInfo
from aas_editor.utils.util_type import isIterable


class ImportTreeViewItem(PackTreeViewItem):
    def __init__(self, obj, parent, **kwargs):
        StandardItem.__init__(self, obj, parent=parent, **kwargs)
        if isinstance(obj, Package):
            self.typehint = Package
            self.package = obj
        else:
            self.package = parent.data(PACKAGE_ROLE)

        try:
            if isinstance(obj, AASReference):
                obj = obj.resolve(self.package.objStore)
        except KeyError as e:
            print(e)
        # if not isinstance(obj, (Package, GeneratorType, DictSupplementaryFileContainer)):
        #     preobj = PreObjectImport.fromObject(obj)
        #     setattr(obj, PREOBJECT_ATTR, preobj)
        self.obj = obj
        self.populate()

    def populate(self):
        kwargs = {
            "parent": self,
            "new": self.new,
        }
        if ClassesInfo.hasPackViewAttrs(type(self.obj)):
            for attr in ClassesInfo.packViewAttrs(type(self.obj)):
                # set package objStore as obj, so that delete works
                itemObj = getattr(self.obj, attr)
                packItem = ImportTreeViewItem(itemObj, name=attr, **kwargs)
                if isinstance(itemObj, GeneratorType):
                    packItem.obj = self.obj.objStore
        elif isIterable(self.obj):
            if isinstance(self.obj, DictSupplementaryFileContainer):
                self._populateFileContainer(self.obj, **kwargs)
            else:
                self._populateIterable(self.obj, **kwargs)

    @staticmethod
    def _populateIterable(obj, **kwargs):
        for sub_item_obj in obj:
            ImportTreeViewItem(sub_item_obj, **kwargs)


    # def _getEditRoleData(self, column, column_name):
    #     if column == ATTRIBUTE_COLUMN:
    #         if hasattr(self.obj, PREOBJECT_ATTR):
    #             return getattr(self.obj, PREOBJECT_ATTR)
    #         return self.obj
    #     if column == VALUE_COLUMN:
    #         if hasattr(self.obj, PREOBJECT_ATTR):
    #             return getattr(self.obj, PREOBJECT_ATTR)
    #         return self.obj
    #     if column_name:
    #         try:
    #             if hasattr(self.obj, PREOBJECT_ATTR):
    #                 preObj = getattr(self.obj, PREOBJECT_ATTR)
    #                 if column_name in preObj.kwargs:
    #                     return preObj.kwargs[column_name]
    #             return getattr(self.obj, column_name)
    #         except AttributeError:
    #             return QVariant()

    # def replItemWithDialog(self, index, objTypeHint, objVal=None, title="", rmDefParams=False):
    #     title = title if title else f"Edit {index.data(NAME_ROLE)}"
    #     try:
    #         objVal = index.data(Qt.)
    #         dialog = dialogs.AddObjDialog(objTypeHint, self, rmDefParams=rmDefParams, objVal=objVal, title=title)
    #     except Exception as e:
    #         QMessageBox.critical(self, "Error", str(e))
    #         return False
    #     result = False
    #     while not result and dialog.exec_() == QDialog.Accepted:
    #         try:
    #             obj = dialog.getObj2add()
    #         except Exception as e:
    #             QMessageBox.critical(self, "Error", str(e))
    #             continue
    #
    #         result = self.model().setData(index, obj, Qt.EditRole)
    #     if dialog.result() == QDialog.Rejected:
    #         print("Item editing cancelled")
    #     dialog.deleteLater()
    #     self.setFocus()
    #     self.setCurrentIndex(index)
    #     return result
