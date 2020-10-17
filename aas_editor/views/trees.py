from collections import Iterable

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt, QItemSelectionModel, QModelIndex
from PyQt5.QtGui import QMouseEvent, QKeyEvent, QKeySequence
from PyQt5.QtWidgets import QTreeView, QMenu, QAbstractItemView, QAction, QDialog, QSizePolicy, \
    QFrame, QAbstractScrollArea, QShortcut
from aas.model import AssetAdministrationShell, Asset, Submodel, SubmodelElement

from aas_editor.dialogs import AddObjDialog
from aas_editor.qcomboboxenumdelegate import QComboBoxEnumDelegate
from aas_editor.models import VALUE_COLUMN, NAME_ROLE, OBJECT_ROLE, PACKAGE_ROLE, ATTRIBUTE_COLUMN, \
    PackTreeViewItem, DetailedInfoItem, DetailedInfoTable, Package
from aas_editor.settings import ATTR_COLUMN_WIDTH
from aas_editor.util import getAttrTypeHint, issubtype, getDefaultVal


class TreeView(QTreeView):
    wheelClicked = pyqtSignal(['QModelIndex'])
    openInCurrTabClicked = pyqtSignal(['QModelIndex'])
    openInNewTabClicked = pyqtSignal(['QModelIndex'])
    openInBackgroundTabClicked = pyqtSignal(['QModelIndex'])

    def __init__(self, parent=None):
        super(TreeView, self).__init__(parent)
        self.attrsMenu = QMenu(self)
        self._initMenu()
        self.customContextMenuRequested.connect(self.openDetailInfoItemMenu)

    # noinspection PyArgumentList
    def _initMenu(self):
        self.addAct = QAction("&Add", self,
                              statusTip="Add item to selected",
                              shortcut=QKeySequence.New,
                              triggered=self._addHandler,
                              enabled=False)

        self.delClearAct = QAction("Delete/clear", self,
                                   shortcut=QKeySequence.Delete,
                                   statusTip="Delete/clear selected item",
                                   triggered=self._delClearHandler,
                                   enabled=True)

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

    def openDetailInfoItemMenu(self, point):
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
                nextRow = nextRow - 1
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
        elif event.key() == Qt.Key_Delete:
            try:
                self.delClearAct.trigger()
            except AttributeError:
                pass
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

    def addItemWithDialog(self, parent: QModelIndex, objType, objName="", objVal=None, windowTitle="", rmDefParams=False):
        dialog = AddObjDialog(objType, self, rmDefParams=rmDefParams, objName=objName, objVal=objVal, windowTitle=windowTitle)
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

    def _upgradeMenu(self):
        menuActions = self.attrsMenu.actions()

        self.addAct.setEnabled(True)

        self.openInCurrTabAct.triggered.connect(lambda: self.openInCurrTabClicked.emit(self.currentIndex()))
        self.openInNewTabAct.triggered.connect(lambda: self.openInNewTabClicked.emit(self.currentIndex()))
        self.openInBackgroundAct.triggered.connect(lambda: self.openInBackgroundTabClicked.emit(self.currentIndex()))

    def _addHandler(self):
        index = self.currentIndex()
        attribute = index.data(NAME_ROLE)
        if isinstance(index.data(OBJECT_ROLE), Package) or not index.isValid():
            self.addItemWithDialog(QModelIndex(), Package)
        elif attribute == "shells":
            self.addItemWithDialog(index, AssetAdministrationShell, rmDefParams=True)
        elif attribute == "assets":
            self.addItemWithDialog(index, Asset, rmDefParams=True)
        elif attribute == "submodels":
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
        menuActions = self.attrsMenu.actions()

        self.editCreateAct = QAction("E&dit/create in dialog", self,
                                     shortcut="Ctrl+E",
                                     statusTip="Edit/create selected item in dialog",
                                     triggered=self._editCreateHandler,
                                     enabled=False)

        self.editAct = QAction("&Edit", self,
                               statusTip="Edit selected item",
                               shortcut="Enter",
                               triggered=lambda: self.edit(self.currentIndex()),
                               enabled=False)

        self.attrsMenu.insertActions(menuActions[0], (self.editAct, self.editCreateAct))

        self.openInCurrTabAct.triggered.connect(lambda: self.openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN), newTab=False))
        self.openInNewTabAct.triggered.connect(lambda: self.openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN)))
        self.openInBackgroundAct.triggered.connect(lambda: self.openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN), setCurrent=False))

    def _buildHandlers(self):
        self.setItemDelegate(QComboBoxEnumDelegate())
        self.clicked.connect(self.openRef)
        self.wheelClicked.connect(lambda refItem: self.openRef(refItem, newTab=True, setCurrent=False))

    def _buildHandlersForNewItem(self):
        self.model().valueChangeFailed.connect(self.parent().itemDataChangeFailed)
        self.selectionModel().currentChanged.connect(self._updateDetailInfoItemMenu)

    def _updateDetailInfoItemMenu(self, index: QModelIndex):
        # update edit/create action
        self.editCreateAct.setEnabled(True)

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

    def _addHandler(self):
        index = self.currentIndex()
        attribute = index.data(NAME_ROLE)
        attrType = getAttrTypeHint(type(self.model().objByIndex(index).parentObj), attribute)
        self.addItemWithDialog(index, attrType)

    def _editCreateHandler(self):
        index = self.currentIndex()
        attribute = index.data(NAME_ROLE)
        attrType = getAttrTypeHint(type(self.model().objByIndex(index).parentObj), attribute)
        self.replItemWithDialog(index, attrType, objVal=index.data(OBJECT_ROLE))

    def replItemWithDialog(self, index, objType, objVal=None, windowTitle=""):
        objName = index.data(NAME_ROLE)
        windowTitle = windowTitle if windowTitle else f"Edit {objName}"
        dialog = AddObjDialog(objType, self, rmDefParams=False, objName=objName, objVal=objVal, windowTitle=windowTitle)
        if dialog.exec_() == QDialog.Accepted:
            obj = dialog.getObj2add()
            self.model().setData(index, obj, Qt.EditRole)
            self.setFocus()
            self.setCurrentIndex(index)
        else:
            print("Item editing cancelled")
        dialog.deleteLater()

    def _newPackItem(self, packItem):
        self._initTreeView(packItem)
        self._buildHandlersForNewItem()

    def openRef(self, detailInfoItem: QModelIndex, newTab=True, setCurrent=True): # todo reimplement search func findItemByObj
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