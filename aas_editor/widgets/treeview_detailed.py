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

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QAction, QAbstractScrollArea, QAbstractItemView, QMessageBox

from aas_editor.models import DetailedInfoTable
from aas_editor.delegates import EditDelegate
from aas_editor.settings import EMPTY_VALUES
from aas_editor.settings.app_settings import ATTR_COLUMN_WIDTH, NAME_ROLE, ATTRIBUTE_COLUMN, \
    VALUE_COLUMN, LINKED_ITEM_ROLE, IS_LINK_ROLE, PARENT_OBJ_ROLE, OBJECT_ROLE
from aas_editor.utils.util_type import getAttrTypeHint, isoftype
from aas_editor.widgets import TreeView


class AttrsTreeView(TreeView):
    def __init__(self, parent=None, treeModel = DetailedInfoTable, **kwargs):
        super(AttrsTreeView, self).__init__(parent, **kwargs)
        self.treeModel = treeModel

    # noinspection PyUnresolvedReferences
    def newPackItem(self, packItem):
        self.initTreeView(packItem)

    def initTreeView(self, packItem):
        self.setExpandsOnDoubleClick(False)
        self.setBaseSize(QtCore.QSize(429, 555))
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.setObjectName("attrsTreeView")
        self.setModelWithProxy(self.treeModel(packItem))
        self.setColumnWidth(ATTRIBUTE_COLUMN, ATTR_COLUMN_WIDTH)
        self.setItemDelegate(EditDelegate(self))

    def buildHandlers(self):
        super(AttrsTreeView, self).buildHandlers()
        self.setItemDelegate(EditDelegate(self))
        self.clicked.connect(self.openRef)
        self.wheelClicked.connect(lambda refItem: self.openRef(refItem, setCurrent=False))

    # noinspection PyArgumentList
    def initMenu(self):
        super(AttrsTreeView, self).initMenu()
        self.openInCurrTabAct.triggered.connect(
            lambda: self.openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN), newTab=False))
        self.openInNewTabAct.triggered.connect(
            lambda: self.openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN)))
        self.openInBackgroundAct.triggered.connect(
            lambda: self.openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN), setCurrent=False))
        self.openInNewWindowAct.triggered.connect(
            lambda: self.openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN), newWindow=True))

    def updateActions(self, index: QModelIndex):
        super().updateActions(index)
        # update open actions
        indexIsLink = bool(index.data(IS_LINK_ROLE))
        self.openInCurrTabAct.setEnabled(indexIsLink)
        self.openInBackgroundAct.setEnabled(indexIsLink)
        self.openInNewTabAct.setEnabled(indexIsLink)
        self.openInNewWindowAct.setEnabled(indexIsLink)

        self.openInCurrTabAct.setVisible(indexIsLink)
        self.openInBackgroundAct.setVisible(indexIsLink)
        self.openInNewTabAct.setVisible(indexIsLink)
        self.openInNewWindowAct.setVisible(indexIsLink)

    def updateEditActs(self, index: QModelIndex):
        super().updateEditActs(index)
        # update edit action
        valColIndex = index.siblingAtColumn(VALUE_COLUMN)
        if valColIndex.flags() & Qt.ItemIsEditable:
            self.setCurrentIndex(valColIndex)
            self.editCreateInDialogAct.setEnabled(True)
        if self.isEditableInsideCell(valColIndex):
            self.setCurrentIndex(valColIndex)
            self.editAct.setEnabled(True)

    def onAddAct(self, objVal=None):
        try:
            index = self.currentIndex()
            attribute = index.data(NAME_ROLE)
            attrTypeHint = getAttrTypeHint(type(index.data(PARENT_OBJ_ROLE)), attribute) #FIXME
            if objVal:
                self.addItemWithDialog(index, attrTypeHint, objVal=objVal, title=f"Add {attribute} element")
            else:
                self.addItemWithDialog(index, attrTypeHint, title=f"Add {attribute} element")
        except Exception as e:
            print(e)
            QMessageBox.critical(self, "Error", str(e))

    def onEditCreate(self, objVal, index=QModelIndex()):
        """
        :param objVal: value to set in dialog input widgets
        :raise KeyError if no typehint found and no objVal was given
        """
        if not index.isValid():
            index = self.currentIndex()
        if index.isValid():
            objVal = objVal if objVal else index.siblingAtColumn(VALUE_COLUMN).data(Qt.EditRole)
            attribute = index.data(NAME_ROLE)
            parentObj = index.data(PARENT_OBJ_ROLE)
            try:
                attrTypeHint = getAttrTypeHint(type(parentObj), attribute)
            except KeyError as e:
                if objVal:
                    attrTypeHint = type(objVal)
                else:
                    raise KeyError("No typehint found for the given item", attribute)
            self.replItemWithDialog(index, attrTypeHint, title=f"Edit/Create {attribute}", objVal=objVal)

    def currentIndex(self) -> QtCore.QModelIndex:
        return super(AttrsTreeView, self).currentIndex().siblingAtColumn(VALUE_COLUMN)

    def isEditableInsideCell(self, index: QModelIndex):
        data = index.data(OBJECT_ROLE)
        if index.siblingAtColumn(VALUE_COLUMN).flags() & Qt.ItemIsEditable \
                and isoftype(data, self.itemDelegate().editableTypesInTable) \
                and data not in EMPTY_VALUES:
            return True
        else:
            return False

    def openRef(self, detailInfoItem: QModelIndex, newTab=True, setCurrent=True, newWindow=False):
        """Open referenced item if clicked on Reference and item is saved locally"""
        if detailInfoItem.column() == VALUE_COLUMN and detailInfoItem.data(IS_LINK_ROLE):
            linkedPackItem = detailInfoItem.data(LINKED_ITEM_ROLE)
            if newWindow:
                self.openInNewWindowClicked.emit(linkedPackItem)
            elif newTab and setCurrent:
                self.openInNewTabClicked.emit(linkedPackItem)
            elif newTab and not setCurrent:
                self.openInBgTabClicked.emit(linkedPackItem)
            else:
                self.openInCurrTabClicked.emit(linkedPackItem)


