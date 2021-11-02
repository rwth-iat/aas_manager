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
from PyQt5.QtGui import QMouseEvent, QKeyEvent
from PyQt5.QtWidgets import QAction, QAbstractScrollArea, QAbstractItemView, QMessageBox

from aas_editor.models import DetailedInfoTable
from aas_editor.delegates import EditDelegate
from aas_editor.settings import EMPTY_VALUES
from aas_editor.settings.app_settings import ATTR_COLUMN_WIDTH, NAME_ROLE, OBJECT_ROLE, ATTRIBUTE_COLUMN, \
    VALUE_COLUMN, LINKED_ITEM_ROLE, IS_LINK_ROLE, PARENT_OBJ_ROLE
from aas_editor.settings.icon_settings import EDIT_ICON
from aas_editor.utils.util_type import getAttrTypeHint
from aas_editor.widgets import TreeView


class AttrsTreeView(TreeView):
    def __init__(self, parent):
        super(AttrsTreeView, self).__init__(parent)

    # noinspection PyUnresolvedReferences
    def newPackItem(self, packItem):
        self.initTreeView(packItem)

    def initTreeView(self, packItem):
        self.setExpandsOnDoubleClick(False)
        self.setBaseSize(QtCore.QSize(429, 555))
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.setObjectName("attrsTreeView")
        self.setModelWithProxy(DetailedInfoTable(packItem))
        self.setColumnWidth(ATTRIBUTE_COLUMN, ATTR_COLUMN_WIDTH)
        self.setItemDelegate(EditDelegate())

    def buildHandlers(self):
        super(AttrsTreeView, self).buildHandlers()
        self.setItemDelegate(EditDelegate())
        self.clicked.connect(self.openRef)
        self.wheelClicked.connect(lambda refItem: self.openRef(refItem, setCurrent=False))

    # noinspection PyArgumentList
    def initMenu(self):
        super(AttrsTreeView, self).initMenu()
        self.editCreateInDialogAct = QAction("E&dit/create in dialog", self,
                                             icon=EDIT_ICON,
                                             statusTip="Edit/create selected item in dialog",
                                             shortcut=Qt.CTRL+Qt.Key_E,
                                             shortcutContext=Qt.WidgetWithChildrenShortcut,
                                             triggered=self.editCreateInDialog,
                                             enabled=True)
        self.addAction(self.editCreateInDialogAct)

        self.editAct = QAction("&Edit", self,
                               statusTip="Edit selected item",
                               shortcut=Qt.Key_Enter,
                               triggered=lambda: self.edit(self.currentIndex()),
                               enabled=False)

        self.attrsMenu.insertActions(self.addAct, (self.editAct, self.editCreateInDialogAct))

        self.openInCurrTabAct.triggered.connect(
            lambda: self.openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN), newTab=False))
        self.openInNewTabAct.triggered.connect(
            lambda: self.openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN)))
        self.openInBackgroundAct.triggered.connect(
            lambda: self.openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN), setCurrent=False))
        self.openInNewWindowAct.triggered.connect(
            lambda: self.openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN), newWindow=True))

    def updateActions(self, index: QModelIndex):
        super(AttrsTreeView, self).updateActions(index)

        # update edit action
        if index.flags() & Qt.ItemIsEditable:
            self.editAct.setEnabled(True)
        elif index.siblingAtColumn(VALUE_COLUMN).flags() & Qt.ItemIsEditable:
            valColIndex = index.siblingAtColumn(VALUE_COLUMN)
            self.setCurrentIndex(valColIndex)
            self.editAct.setEnabled(True)
        else:
            self.editAct.setEnabled(False)

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

    def onAddAct(self, objVal=None):
        try:
            index = self.currentIndex()
            attribute = index.data(NAME_ROLE)
            attrType = getAttrTypeHint(type(index.data(PARENT_OBJ_ROLE)), attribute) #FIXME
            if objVal:
                self.addItemWithDialog(index, attrType, objVal=objVal, title=f"Add {attribute} element", rmDefParams=True)
            else:
                self.addItemWithDialog(index, attrType, title=f"Add {attribute} element", rmDefParams=True)
        except Exception as e:
            print(e)
            QMessageBox.critical(self, "Error", str(e))

    def editCreateInDialog(self, objVal=None):
        try:
            self.onEditCreate(objVal)
        except Exception as e:
            print(e)
            QMessageBox.critical(self, "Error", str(e))

    def onEditCreate(self, objVal=None):
        """
        :param objVal: value to set in dialog input widgets
        :raise KeyError if no typehint found and no objVal was given
        """
        index = self.currentIndex()
        if index.isValid():
            objVal = objVal if objVal else index.data(OBJECT_ROLE)
            attribute = index.data(NAME_ROLE)
            try:
                attrType = getAttrTypeHint(type(index.data(PARENT_OBJ_ROLE)), attribute)
            except KeyError as e:
                if objVal:
                    attrType = type(objVal)
                else:
                    raise KeyError("No typehint found for the given item", index.data(NAME_ROLE))
            self.replItemWithDialog(index, attrType, title=f"Edit/Create {attribute}", objVal=objVal)

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

    def mouseDoubleClickEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.LeftButton:
            self.onDoubleClickEvent()
        else:
            super(TreeView, self).mouseDoubleClickEvent(e)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.state() == QAbstractItemView.EditingState:
                # if we are editing, inform base
                super(TreeView, self).keyPressEvent(event)
            else:
                self.onEnterEvent()
        else:
            # any other key was pressed, inform base
            super(TreeView, self).keyPressEvent(event)

    def onEnterEvent(self):
        index = self.currentIndex()
        # if we're not editing, check if editable and start editing or expand/collapse
        if index.siblingAtColumn(VALUE_COLUMN).flags() & Qt.ItemIsEditable:
            if index.data(OBJECT_ROLE) in EMPTY_VALUES:
                self.editCreateInDialog()
            else:
                self.edit(index)
        else:
            self.toggleFold(index)

    def onDoubleClickEvent(self):
        index = self.currentIndex()
        # if we're not editing, check if editable and start editing or expand/collapse
        if index.flags() & Qt.ItemIsEditable:
            if index.data(OBJECT_ROLE) in EMPTY_VALUES:
                self.editCreateInDialog()
            else:
                self.edit(index)
        else:
            self.toggleFold(index)

    def toggleFold(self, index: QModelIndex):
        index = index.siblingAtColumn(0)
        if self.isExpanded(index):
            self.collapse(index)
        else:
            self.expand(index)