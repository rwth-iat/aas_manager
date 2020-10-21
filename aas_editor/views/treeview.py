import codecs
import pickle
from typing import Iterable

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt, QModelIndex
from PyQt5.QtGui import QKeySequence, QMouseEvent, QKeyEvent, QClipboard
from PyQt5.QtWidgets import QTreeView, QAction, QMenu, QApplication, QDialog

from aas_editor.dialogs import AddObjDialog, DictItem
from aas_editor.settings import NAME_ROLE, OBJECT_ROLE, VALUE_COLUMN
from aas_editor.util import getDefaultVal


class TreeView(QTreeView):
    wheelClicked = pyqtSignal(['QModelIndex'])
    openInCurrTabClicked = pyqtSignal(['QModelIndex'])
    openInNewTabClicked = pyqtSignal(['QModelIndex'])
    openInBackgroundTabClicked = pyqtSignal(['QModelIndex'])

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
                                        statusTip="Open selected item in current tab")

        self.openInNewTabAct = QAction("Open in new &tab", self,
                                       statusTip="Open selected item in new tab")

        self.openInBackgroundAct = QAction("Open in &background tab", self,
                                           statusTip="Open selected item in background tab")

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
        self.foldingMenu = self.attrsMenu.addMenu("Folding")
        self.foldingMenu.addAction(self.collapseAct)
        self.foldingMenu.addAction(self.collapseRecAct)
        self.foldingMenu.addAction(self.collapseAllAct)
        self.foldingMenu.addAction(self.expandAct)
        self.foldingMenu.addAction(self.expandRecAct)
        self.foldingMenu.addAction(self.expandAllAct)
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
            # we captured the Enter key press, now we need to move to the next row
            # nextRow = self.currentIndex().row() + 1
            # if nextRow+1 > self.model().rowCount(self.currentIndex().parent()):
            #     # we are all the way down, we can 't go any further
            #     nextRow -= 1
            # if self.state() == QAbstractItemView.EditingState:
            #     # if we are editing, confirm and move to the row below
            #     nextIndex = self.currentIndex().siblingAtRow(nextRow).siblingAtColumn(VALUE_COLUMN)
            #     self.setCurrentIndex(nextIndex)
            #     self.selectionModel().select(nextIndex, QItemSelectionModel.ClearAndSelect)
            # else:
                # if we're not editing, check if editable and start editing or expand/collapse
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
        clipboard = QApplication.clipboard()
        pickledObj2copy = codecs.encode(pickle.dumps(index.data(OBJECT_ROLE)), "base64").decode()
        clipboard.setText(pickledObj2copy, QClipboard.Clipboard)

    def _pasteHandler(self):
        try:
            clipboard = QApplication.clipboard()
            text = clipboard.text(QClipboard.Clipboard)
            unpickledObj2paste = pickle.loads(codecs.decode(text.encode(), "base64"))
            try:
                # FIXME
                if self.addAct.isEnabled():
                    self._addHandler(unpickledObj2paste)
                else:
                    raise TypeError()
            except (TypeError, AttributeError) as e:
                print(e)
                self._editCreateHandler(unpickledObj2paste)
        except (TypeError, SyntaxError) as e:
            print(f"Data could not be paste: {e}: {text}")

    def _cutHandler(self):
        self._copyHandler()
        self._delClearHandler()

    def addItemWithDialog(self, parent: QModelIndex, objType, objName="", objVal=None,
                          windowTitle="", rmDefParams=False):
        dialog = AddObjDialog(objType, self, rmDefParams=rmDefParams,
                              objName=objName, objVal=objVal, windowTitle=windowTitle)
        if dialog.exec_() == QDialog.Accepted:
            obj = dialog.getObj2add()
            if isinstance(obj, dict):
                for key, value in obj.items():
                    self.model().addItem(DictItem(key, value), parent)
            elif isinstance(obj, Iterable) and not isinstance(obj, (str, bytes)):
                for i in obj:
                    self.model().addItem(i, parent)
            else:
                self.model().addItem(obj, parent)
            self.setFocus()
            self.setCurrentIndex(parent)
        else:
            print("Item adding cancelled")
        dialog.deleteLater()