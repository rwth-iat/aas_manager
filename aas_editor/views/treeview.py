import codecs
import pickle
from typing import Iterable

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt, QModelIndex
from PyQt5.QtGui import QKeySequence, QMouseEvent, QKeyEvent, QClipboard
from PyQt5.QtWidgets import QTreeView, QAction, QMenu, QApplication, QDialog

from aas_editor.dialogs import AddObjDialog
from aas_editor.models import DictItem
from aas_editor.settings import NAME_ROLE, OBJECT_ROLE, VALUE_COLUMN
from aas_editor.util import getDefaultVal, isIterable, getReqParams4init, isoftype, getTypeHint


class TreeView(QTreeView):
    wheelClicked = pyqtSignal(['QModelIndex'])
    openInCurrTabClicked = pyqtSignal(['QModelIndex'])
    openInNewTabClicked = pyqtSignal(['QModelIndex'])
    openInBackgroundTabClicked = pyqtSignal(['QModelIndex'])

    treeObjClipboard = []

    def __init__(self, parent=None):
        super(TreeView, self).__init__(parent)
        self.createActions()
        self.createMenu()
        self.customContextMenuRequested.connect(self.openMenu)

    # noinspection PyArgumentList
    def createActions(self):
        self.copyAct = QAction("Copy", self,
                               statusTip="Copy selected item",
                               shortcut=QKeySequence.Copy,
                               shortcutContext=Qt.WidgetWithChildrenShortcut,
                               triggered=self._copyHandler,
                               enabled=True)
        self.addAction(self.copyAct)

        self.pasteAct = QAction("Paste", self,
                                statusTip="Paste from clipboard",
                                shortcut=QKeySequence.Paste,
                                shortcutContext=Qt.WidgetWithChildrenShortcut,
                                triggered=self._pasteHandler,
                                enabled=True)
        self.addAction(self.pasteAct)

        self.cutAct = QAction("Cut", self,
                              statusTip="Cut selected item",
                              shortcut=QKeySequence.Cut,
                              shortcutContext=Qt.WidgetWithChildrenShortcut,
                              triggered=self._cutHandler,
                              enabled=True)
        self.addAction(self.cutAct)

        self.addAct = QAction("&Add", self,
                              statusTip="Add item to selected",
                              shortcut=QKeySequence.New,
                              shortcutContext=Qt.WidgetWithChildrenShortcut,
                              triggered=self._addHandler,
                              enabled=False)
        self.addAction(self.addAct)

        self.delClearAct = QAction("Delete/clear", self,
                                   statusTip="Delete/clear selected item",
                                   shortcut=QKeySequence.Delete,
                                   shortcutContext=Qt.WidgetWithChildrenShortcut,
                                   triggered=self._delClearHandler,
                                   enabled=True)
        self.addAction(self.delClearAct)

        self.collapseAct = QAction("Collapse", self,
                                   statusTip="Collapse selected item",
                                   triggered=lambda: self.collapse(self.currentIndex()))

        self.collapseRecAct = QAction("Collapse recursively", self,
                                      statusTip="Collapse recursively selected item",
                                      triggered=lambda: self.collapse(self.currentIndex()))

        self.collapseAllAct = QAction("Collapse all", self,
                                      statusTip="Collapse all items",
                                      triggered=self.collapseAll)

        self.expandAct = QAction("Expand", self,
                                 statusTip="Expand selected item",
                                 triggered=lambda: self.expand(self.currentIndex()))

        self.expandRecAct = QAction("Expand recursively", self,
                                    statusTip="Expand recursively selected item",
                                    triggered=lambda: self.expandRecursively(self.currentIndex()))

        self.expandAllAct = QAction("Expand all", self,
                                    statusTip="Expand all items",
                                    triggered=self.expandAll)

        self.openInCurrTabAct = QAction("Open in current ta&b", self,
                                        statusTip="Open selected item in current tab",
                                        enabled=False)

        self.openInNewTabAct = QAction("Open in new &tab", self,
                                       statusTip="Open selected item in new tab",
                                       enabled=False)

        self.openInBackgroundAct = QAction("Open in &background tab", self,
                                           statusTip="Open selected item in background tab",
                                           enabled=False)

    def createMenu(self) -> None:
        self.attrsMenu = QMenu(self)
        self.attrsMenu.addAction(self.cutAct)
        self.attrsMenu.addAction(self.copyAct)
        self.attrsMenu.addAction(self.pasteAct)
        self.attrsMenu.addSeparator()
        self.attrsMenu.addAction(self.addAct)
        self.attrsMenu.addSeparator()
        self.attrsMenu.addAction(self.delClearAct)
        self.attrsMenu.addSeparator()
        foldingMenu = self.attrsMenu.addMenu("Folding")
        foldingMenu.addAction(self.collapseAct)
        foldingMenu.addAction(self.collapseRecAct)
        foldingMenu.addAction(self.collapseAllAct)
        foldingMenu.addAction(self.expandAct)
        foldingMenu.addAction(self.expandRecAct)
        foldingMenu.addAction(self.expandAllAct)
        self.attrsMenu.addSeparator()
        self.attrsMenu.addAction(self.openInCurrTabAct)
        self.attrsMenu.addAction(self.openInNewTabAct)
        self.attrsMenu.addAction(self.openInBackgroundAct)

    def openMenu(self, point):
        self.attrsMenu.exec_(self.viewport().mapToGlobal(point))

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.MiddleButton:
            self.wheelClicked.emit(self.indexAt(e.pos()))
        else:
            super(TreeView, self).mousePressEvent(e)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            index2edit = self.currentIndex().siblingAtColumn(VALUE_COLUMN)
            if index2edit.flags() & Qt.ItemIsEditable:
                if index2edit.data(OBJECT_ROLE) is None:
                    self._editCreateHandler()
                else:
                    self.edit(index2edit)
            else:
                index2fold = self.currentIndex().siblingAtColumn(0)
                if self.isExpanded(index2fold):
                    self.collapse(index2fold)
                else:
                    self.expand(index2fold)
        else:
            # any other key was pressed, inform base
            super(TreeView, self).keyPressEvent(event)

    def collapse(self, index: QtCore.QModelIndex) -> None:
        newIndex = index.siblingAtColumn(0)
        super(TreeView, self).collapse(newIndex)

    def expand(self, index: QtCore.QModelIndex) -> None:
        newIndex = index.siblingAtColumn(0)
        super(TreeView, self).expand(newIndex)

    def _delClearHandler(self):
        index = self.currentIndex()
        attribute = index.data(NAME_ROLE)
        try:
            parentObjType = type(self.model().objByIndex(index).parentObj)
            defaultVal = getDefaultVal(attribute, parentObjType)
            self.model().clearRow(index.row(), index.parent(), defaultVal)
        except (AttributeError, IndexError):
            self.model().clearRow(index.row(), index.parent())

    def _copyHandler(self):
        index = self.currentIndex()
        self.treeObjClipboard.clear()
        self.treeObjClipboard.append(index.data(OBJECT_ROLE))
        clipboard = QApplication.clipboard()
        clipboard.setText(index.data(Qt.DisplayRole), QClipboard.Clipboard)
        if self._isPasteOk(index):
            self.pasteAct.setEnabled(True)
        else:
            self.pasteAct.setEnabled(False)

    def _pasteHandler(self):
        obj2paste = self.treeObjClipboard[0]
        index = self.currentIndex()
        reqAttrsDict = getReqParams4init(type(obj2paste), rmDefParams=True)

        # if no req. attrs, paste data without dialog
        if not reqAttrsDict:
            if isIterable(index.parent().data(OBJECT_ROLE)) and not isIterable(obj2paste):
                self.model().addItem(obj2paste, index.parent())
            else:
                self.model().setData(index, obj2paste, Qt.EditRole)
        # if req. attrs, paste data with dialog for asking to check req. attrs
        else:
            if isIterable(index.parent().data(OBJECT_ROLE)) and not isIterable(obj2paste):
                self.addItemWithDialog(index.parent(), type(obj2paste), objVal=obj2paste, title=f"Paste element", rmDefParams=True)
            else:
                self.replItemWithDialog(index, type(obj2paste), objVal=obj2paste, title=f"Paste element", rmDefParams=True)

    def _cutHandler(self):
        self._copyHandler()
        self._delClearHandler()

    def addItemWithDialog(self, parent: QModelIndex, objType, objVal=None,
                          title="", rmDefParams=False):
        dialog = AddObjDialog(objType, self, rmDefParams=rmDefParams,
                              objVal=objVal, title=title)
        if dialog.exec_() == QDialog.Accepted:
            obj = dialog.getObj2add()
            if isinstance(obj, dict):
                for key, value in obj.items():
                    self.model().addItem(DictItem(key, value), parent)
            elif isIterable(obj):
                for i in obj:
                    self.model().addItem(i, parent)
            else:
                self.model().addItem(obj, parent)
            self.setFocus()
            self.setCurrentIndex(parent)
        else:
            print("Item adding cancelled")
        dialog.deleteLater()

    def replItemWithDialog(self, index, objType, objVal=None, title="", rmDefParams=False):
        title = title if title else f"Edit {index.data(NAME_ROLE)}"
        dialog = AddObjDialog(objType, self, rmDefParams=rmDefParams, objVal=objVal, title=title)
        if dialog.exec_() == QDialog.Accepted:
            obj = dialog.getObj2add()
            self.model().setData(index, obj, Qt.EditRole)
            self.setFocus()
            self.setCurrentIndex(index)
        else:
            print("Item editing cancelled")
        dialog.deleteLater()
