from collections import Iterable

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt, QItemSelectionModel, QModelIndex
from PyQt5.QtGui import QMouseEvent, QKeyEvent, QKeySequence, QClipboard
from PyQt5.QtWidgets import QTreeView, QMenu, QAbstractItemView, QAction, QDialog, QSizePolicy, \
    QFrame, QAbstractScrollArea, QApplication
from aas.model import AssetAdministrationShell, Asset, Submodel, SubmodelElement

from aas_editor.dialogs import AddObjDialog
from aas_editor.qcomboboxenumdelegate import QComboBoxEnumDelegate
from aas_editor.models import VALUE_COLUMN, NAME_ROLE, OBJECT_ROLE, ATTRIBUTE_COLUMN, \
     DetailedInfoTable, Package
from aas_editor.settings import ATTR_COLUMN_WIDTH
from aas_editor.util import getAttrTypeHint, issubtype, getDefaultVal

from aas.model.aas import *
from aas.model.base import *
from aas.model.concept import *
from aas.model.provider import *
from aas.model.submodel import *


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
                              triggered=self._pasteHandler,
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
            nextRow = self.currentIndex().row() + 1
            if nextRow+1 > self.model().rowCount(self.currentIndex().parent()):
                # we are all the way down, we can 't go any further
                nextRow -= 1
            if self.state() == QAbstractItemView.EditingState:
                # if we are editing, confirm and move to the row below
                nextIndex = self.currentIndex().siblingAtRow(nextRow)
                self.setCurrentIndex(nextIndex)
                self.selectionModel().select(nextIndex, QItemSelectionModel.ClearAndSelect)
            else:
                # if we're not editing, check if editable and start editing or expand/collapse
                index2edit = self.currentIndex().siblingAtColumn(VALUE_COLUMN)
                if index2edit.flags() & Qt.ItemIsEditable:
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
        clipboard.setText(repr(index.data(OBJECT_ROLE)), QClipboard.Clipboard)

    def _pasteHandler(self):
        try:
            clipboard = QApplication.clipboard()
            text = clipboard.text(QClipboard.Clipboard)
            objToPaste = eval(text)
            try:
                self._addHandler(list(objToPaste))
            except TypeError:
                self._editCreateHandler(objToPaste)
        except (TypeError, SyntaxError):
            print(f"Data could not be paste: {text}")

    def _cutHandler(self):
        self._copyHandler()
        self._delClearHandler()

    def addItemWithDialog(self, parent: QModelIndex, objType, objName="", objVal=None,
                          windowTitle="", rmDefParams=False):
        dialog = AddObjDialog(objType, self, rmDefParams=rmDefParams,
                              objName=objName, objVal=objVal, windowTitle=windowTitle)
        if dialog.exec_() == QDialog.Accepted:
            obj = dialog.getObj2add()
            self.model().addItem(obj, parent)
            self.setFocus()
            self.setCurrentIndex(parent)
        else:
            print("Item adding cancelled")
        dialog.deleteLater()


class PackTreeView(TreeView):
    """Singleton class"""
    __instance = None

    @staticmethod
    def instance() -> 'PackTreeView':
        """Instance access method"""
        if PackTreeView.__instance is None:
            PackTreeView()
        return PackTreeView.__instance

    def __init__(self, parent=None):
        if PackTreeView.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            super(PackTreeView, self).__init__(parent)
            PackTreeView.__instance = self
            self._upgradeMenu()

    # noinspection PyUnresolvedReferences
    def _upgradeMenu(self):
        self.openInCurrTabAct.triggered.connect(
            lambda: self.openInCurrTabClicked.emit(self.currentIndex()))
        self.openInNewTabAct.triggered.connect(
            lambda: self.openInNewTabClicked.emit(self.currentIndex()))
        self.openInBackgroundAct.triggered.connect(
            lambda: self.openInBackgroundTabClicked.emit(self.currentIndex()))

    def setModel(self, model: QtCore.QAbstractItemModel) -> None:
        super(PackTreeView, self).setModel(model)
        self.selectionModel().currentChanged.connect(self._updateMenu)

    def _updateMenu(self, index: QModelIndex):
        # update add action
        obj = index.data(OBJECT_ROLE)
        if isinstance(obj, (Iterable, Submodel, Package)) or not index.isValid():
            self.addAct.setEnabled(True)
        else:
            self.addAct.setEnabled(False)

    def _addHandler(self):
        index = self.currentIndex()
        name = index.data(NAME_ROLE)
        if isinstance(index.data(OBJECT_ROLE), Package) or not index.isValid():
            self.addItemWithDialog(QModelIndex(), Package)
        elif name == "shells":
            self.addItemWithDialog(index, AssetAdministrationShell, rmDefParams=True)
        elif name == "assets":
            self.addItemWithDialog(index, Asset, rmDefParams=True)
        elif name == "submodels":
            self.addItemWithDialog(index, Submodel, rmDefParams=True)
        elif isinstance(index.data(OBJECT_ROLE), Submodel):
            self.addItemWithDialog(index, SubmodelElement, rmDefParams=True)


class AttrsTreeView(TreeView):
    def __init__(self, parent):
        super(AttrsTreeView, self).__init__(parent)
        self._upgradeMenu()
        self._buildHandlers()
        self.packTreeView: PackTreeView = PackTreeView.instance()

    # noinspection PyArgumentList
    def _upgradeMenu(self):
        self.editCreateAct = QAction("E&dit/create in dialog", self,
                                     statusTip="Edit/create selected item in dialog",
                                     shortcut=Qt.CTRL+Qt.Key_E,
                                     shortcutContext=Qt.WidgetWithChildrenShortcut,
                                     triggered=self._editCreateHandler,
                                     enabled=True)
        self.addAction(self.editCreateAct)

        self.editAct = QAction("&Edit", self,
                               statusTip="Edit selected item",
                               shortcut=Qt.Key_Enter,
                               triggered=lambda: self.edit(self.currentIndex()),
                               enabled=False)

        self.attrsMenu.insertActions(self.addAct, (self.editAct, self.editCreateAct))

        self.openInCurrTabAct.triggered.connect(
            lambda: self.openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN), newTab=False))
        self.openInNewTabAct.triggered.connect(
            lambda: self.openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN)))
        self.openInBackgroundAct.triggered.connect(
            lambda: self.openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN), setCurrent=False))

    # noinspection PyUnresolvedReferences
    def _buildHandlers(self):
        self.setItemDelegate(QComboBoxEnumDelegate())
        self.clicked.connect(self.openRef)
        self.wheelClicked.connect(
            lambda refItem: self.openRef(refItem, setCurrent=False))

    def _buildHandlersForNewItem(self):
        self.model().valueChangeFailed.connect(self.parent().itemDataChangeFailed)
        self.selectionModel().currentChanged.connect(self._updateMenu)

    def _updateMenu(self, index: QModelIndex):
        # update edit action
        if index.flags() & Qt.ItemIsEditable:
            self.editAct.setEnabled(True)
        elif index.siblingAtColumn(VALUE_COLUMN).flags() & Qt.ItemIsEditable:
            valColIndex = index.siblingAtColumn(VALUE_COLUMN)
            self.setCurrentIndex(valColIndex)
            self.editAct.setEnabled(True)
        else:
            self.editAct.setEnabled(False)

        # update add action
        obj = index.data(OBJECT_ROLE)
        if isinstance(obj, Iterable):
            self.addAct.setEnabled(True)
        else:
            self.addAct.setEnabled(False)

        # update open actions
        if self.model().objByIndex(index).isLink:
            self.openInCurrTabAct.setEnabled(True)
            self.openInBackgroundAct.setEnabled(True)
            self.openInNewTabAct.setEnabled(True)
        else:
            self.openInCurrTabAct.setEnabled(False)
            self.openInBackgroundAct.setEnabled(False)
            self.openInNewTabAct.setEnabled(False)

    def _addHandler(self, objVal=None):
        index = self.currentIndex()
        attribute = index.data(NAME_ROLE)
        attrType = getAttrTypeHint(type(self.model().objByIndex(index).parentObj), attribute)
        if objVal:
            self.addItemWithDialog(index, attrType, objVal=objVal, objName=f"{attribute} element")
        else:
            self.addItemWithDialog(index, attrType, objName=f"{attribute} element")

    def _editCreateHandler(self, objVal=None):
        index = self.currentIndex()
        objVal = objVal if objVal else index.data(OBJECT_ROLE)
        attribute = index.data(NAME_ROLE)
        attrType = getAttrTypeHint(type(self.model().objByIndex(index).parentObj), attribute)
        self.replItemWithDialog(index, attrType, objVal=objVal)

    def replItemWithDialog(self, index, objType, objVal=None, windowTitle=""):
        objName = index.data(NAME_ROLE)
        windowTitle = windowTitle if windowTitle else f"Edit {objName}"
        dialog = AddObjDialog(objType, self, rmDefParams=False,
                              objName=objName, objVal=objVal, windowTitle=windowTitle)
        if dialog.exec_() == QDialog.Accepted:
            obj = dialog.getObj2add()
            self.model().setData(index, obj, Qt.EditRole)
            self.setFocus()
            self.setCurrentIndex(index)
        else:
            print("Item editing cancelled")
        dialog.deleteLater()

    # todo reimplement search func findItemByObj
    def openRef(self, detailInfoItem: QModelIndex, newTab=True, setCurrent=True):
        item = self.model().objByIndex(detailInfoItem)
        if detailInfoItem.column() == VALUE_COLUMN and item.isLink:
            obj = item.obj.resolve(item.package.objStore)
            linkedPackItem = self.packTreeView.model().findItemByObj(obj)
            if newTab and setCurrent:
                self.openInNewTabClicked.emit(linkedPackItem)
            elif newTab and not setCurrent:
                self.openInBackgroundTabClicked.emit(linkedPackItem)
            else:
                self.openInCurrTabClicked.emit(linkedPackItem)

    def newPackItem(self, packItem):
        self._initTreeView(packItem)
        self._buildHandlersForNewItem()

    def _initTreeView(self, packItem):
        self.setExpandsOnDoubleClick(False)
        self.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(429, 0))
        self.setBaseSize(QtCore.QSize(429, 555))
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Sunken)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.setObjectName("attrsTreeView")

        attrsModel = DetailedInfoTable(packItem)
        self.setModel(attrsModel)
        self.setColumnWidth(ATTRIBUTE_COLUMN, ATTR_COLUMN_WIDTH)
        self.setItemDelegate(QComboBoxEnumDelegate())
