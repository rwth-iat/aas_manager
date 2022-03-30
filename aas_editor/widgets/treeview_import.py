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
import typing
from pathlib import Path
from typing import Optional

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QModelIndex, QSettings, QPoint
from PyQt5.QtGui import QDropEvent, QDragEnterEvent, QMouseEvent, QColor, QPalette, QPainter, QKeyEvent
from PyQt5.QtWidgets import QAction, QMessageBox, QFileDialog, QStyleOptionViewItem, QMenu, QWidget, QDialog
from basyx.aas.model import AssetAdministrationShell

from aas_editor import dialogs
from aas_editor.delegates import EditDelegate
from aas_editor.package import Package, StoredFile
from aas_editor.kwargPackage import KwargObject, KwargPackage
from aas_editor.settings import FILTER_AAS_FILES, CLASSES_INFO, PACKVIEW_ATTRS_INFO, \
    FILE_TYPE_FILTERS, NOT_GIVEN, EMPTY_VALUES, REFERABLE_INHERITORS_ATTRS
from aas_editor.settings.app_settings import NAME_ROLE, OBJECT_ROLE, PACKAGE_ROLE, MAX_RECENT_FILES, ACPLT, \
    APPLICATION_NAME, OPENED_PACKS_ROLE, OPENED_FILES_ROLE, ADD_ITEM_ROLE, \
    TYPE_ROLE, \
    CLEAR_ROW_ROLE, AppSettings, COLUMN_NAME_ROLE, OBJECT_COLUMN_NAME, OBJECT_VALUE_COLUMN_NAME
from aas_editor.settings.shortcuts import SC_OPEN, SC_SAVE_ALL
from aas_editor.settings.icons import NEW_PACK_ICON, OPEN_ICON, OPEN_DRAG_ICON, SAVE_ICON, SAVE_ALL_ICON, \
    VIEW_ICON
from aas_editor.utils import util_type
from aas_editor.utils.util import getDefaultVal, getReqParams4init
from aas_editor.utils.util_classes import ClassesInfo, DictItem
from aas_editor.utils.util_type import getAttrTypeHint, isoftype, checkType, isSimpleIterable, isIterable
from aas_editor.widgets import TreeView, PackTreeView
from aas_editor.widgets.treeview import HeaderView


class ImportTreeView(PackTreeView):
    def onEditCreate(self, objVal=None, index=QModelIndex()):
        """
        :param objVal: value to set in dialog input widgets
        :raise KeyError if no typehint found and no objVal was given
        """
        if not index.isValid():
            index = self.currentIndex()
        if index.isValid():
            objVal = objVal if objVal else index.data(Qt.EditRole)
            attribute = index.data(COLUMN_NAME_ROLE)
            parentObj = index.data(OBJECT_ROLE)
            try:
                attrType = KwargObject.getAttrTypeHint(parentObj, attribute)
            except KeyError as e:
                if objVal:
                    attrType = type(objVal)
                else:
                    raise KeyError("No typehint found for the given item", attribute)
            self.replItemWithDialog(index, attrType, title=f"Edit/Create {attribute}", objVal=objVal)


    def addItemWithDialog(self, parent: QModelIndex, objType, objVal=None,
                          title="", rmDefParams=False):
        try:
            dialog = dialogs.AddObjDialog(objType, self, rmDefParams=rmDefParams, objVal=objVal, title=title)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return False

        result = False
        while not result and dialog.exec_() == QDialog.Accepted:
            try:
                preobj = dialog.getPreObj()
                if hasattr(preobj, "object"):
                    obj = preobj.object
                else:
                    obj = KwargObject(preobj.objType, preobj.args, preobj.kwargs)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
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


    def updateActions(self, index: QModelIndex):
        super(ImportTreeView, self).updateActions(index)

        # update add action
        obj = index.data(OBJECT_ROLE)
        if isinstance(obj, KwargObject):
            objType = obj.objtype
        else:
            objType = type(obj)
        attrName = index.data(NAME_ROLE)

        if ClassesInfo.addActText(objType):
            addActText = ClassesInfo.addActText(objType)
            enabled = True
        elif attrName in Package.addableAttrs():
            addActText = ClassesInfo.addActText(Package, attrName)
            enabled = True
        elif isIterable(obj):
            addActText = f"Add {attrName} element"
            enabled = True
        else:
            addActText = "Add"
            enabled = False
        self.addAct.setEnabled(enabled)
        self.addAct.setText(addActText)


    def onAddAct(self, objVal=None, parent: QModelIndex = None):
        parent = parent if parent else self.currentIndex()
        name = parent.data(NAME_ROLE)
        parentObj = parent.data(OBJECT_ROLE)

        if objVal:
            kwargs = {"parent": parent,
                      "rmDefParams": False,
                      "objVal": objVal}
        else:
            kwargs = {"parent": parent,
                      "rmDefParams": True}

        try:
            if not parent.isValid():
                self.newPackWithDialog()
            elif name in Package.addableAttrs():
                self.addItemWithDialog(objType=ClassesInfo.addType(Package, name), **kwargs)
            elif ClassesInfo.addType(type(parentObj)):
                self.addItemWithDialog(objType=ClassesInfo.addType(type(parentObj)), **kwargs)
            elif isinstance(parentObj, KwargObject) and ClassesInfo.addType(parentObj.objtype):
                self.addItemWithDialog(objType=ClassesInfo.addType(parentObj.objtype), **kwargs)
            else:
                raise TypeError("Parent type is not extendable:", type(parent.data(OBJECT_ROLE)))
        except Exception as e:
            print(e)
            QMessageBox.critical(self, "Error", str(e))


    def newPackWithDialog(self):
        saved = False
        file = 'new_aas_file.aasx'

        while not saved:
            file, _ = QFileDialog.getSaveFileName(self, 'Create new AAS File', file,
                                                  filter=FILTER_AAS_FILES,
                                                  initialFilter=self.defaultNewFileTypeFilter)
            if file:
                pack = KwargPackage()
                saved = self.savePack(pack, file)
                if saved:
                    self.model().setData(QModelIndex(), pack, ADD_ITEM_ROLE)
            else:
                # cancel pressed
                return