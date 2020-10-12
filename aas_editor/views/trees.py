from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt, QItemSelectionModel, QModelIndex
from PyQt5.QtGui import QMouseEvent, QKeyEvent
from PyQt5.QtWidgets import QTreeView, QMenu, QAbstractItemView, QAction, QDialog, QSizePolicy, \
    QFrame, QAbstractScrollArea
from aas.model import AssetAdministrationShell, Asset, Submodel, SubmodelElement

from aas_editor.dialogs import AddObjDialog
from aas_editor.qcomboboxenumdelegate import QComboBoxEnumDelegate
from aas_editor.models import VALUE_COLUMN, NAME_ROLE, OBJECT_ROLE, PACKAGE_ROLE, ATTRIBUTE_COLUMN, \
    PackTreeViewItem, DetailedInfoItem, DetailedInfoTable, Package
from aas_editor.settings import ATTR_COLUMN_WIDTH
from aas_editor.util import getAttrTypeHint


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

    def _initMenu(self):
        self.attrsMenu.addSeparator()
        self.collapseAct = self.attrsMenu.addAction("C&ollapse", lambda: self.collapse(self.currentIndex()))
        self.expandAct = self.attrsMenu.addAction("E&xpand", lambda: self.expand(self.currentIndex()))
        self.collapseAllAct = self.attrsMenu.addAction("Co&llapse all", self.collapseAll)
        self.expandAllAct = self.attrsMenu.addAction("Ex&pand all", self.expandAll)
        self.attrsMenu.addSeparator()

    def openDetailInfoItemMenu(self, point):
        self.attrsMenu.exec_(self.viewport().mapToGlobal(point))

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.MiddleButton:
            self.wheelClicked.emit(self.indexAt(e.pos()))
        else:
            super(TreeView, self).mousePressEvent(e)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Return:
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
        else:
            # any other key was pressed, inform base
            super(TreeView, self).keyPressEvent(event)

    def collapse(self, index: QtCore.QModelIndex) -> None:
        newIndex = index.siblingAtColumn(0)
        super(TreeView, self).collapse(newIndex)

    def expand(self, index: QtCore.QModelIndex) -> None:
        newIndex = index.siblingAtColumn(0)
        super(TreeView, self).expand(newIndex)


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
            self._updateMenu()

    def _updateMenu(self):
        menuActions = self.attrsMenu.actions()

        self.addAct = QAction("&Add")
        self.addAct.setStatusTip("Add item to selected")
        self.addAct.setEnabled(True)
        self.attrsMenu.insertAction(menuActions[0], self.addAct)

        self.addAct.triggered.connect(self.addHandler)

        self.openInCurrTabAct = self.attrsMenu.addAction("Open in current ta&b", lambda: self.openInCurrTabClicked.emit(self.currentIndex()))
        self.openInNewTabAct = self.attrsMenu.addAction("Open in new &tab", lambda: self.openInNewTabClicked.emit(self.currentIndex()))
        self.openInBackgroundAct = self.attrsMenu.addAction("Open in &background tab", lambda: self.openInBackgroundTabClicked.emit(self.currentIndex()))

    def addHandler(self):
        index = self.currentIndex()
        attribute = index.data(NAME_ROLE)
        if isinstance(index.data(OBJECT_ROLE), Package) or not index.isValid():
            self.addItemWithDialog(QModelIndex(), Package)
        elif attribute == "shells":
            self.addItemWithDialog(index, AssetAdministrationShell)
        elif attribute == "assets":
            self.addItemWithDialog(index, Asset)
        elif attribute == "submodels":
            self.addItemWithDialog(index, Submodel)
        elif isinstance(index.data(OBJECT_ROLE), Submodel):
            self.addItemWithDialog(index, SubmodelElement)

    def addItemWithDialog(self, index, objType, objName="", objVal=None):
        dialog = AddObjDialog(objType, self, objName=objName, objVal=objVal)
        if dialog.exec_() == QDialog.Accepted:
            obj = dialog.getObj2add()
            item = self.model().addItem(PackTreeViewItem(obj=obj), index)
            self.setFocus()
            self.setCurrentIndex(item)
        else:
            print("Item adding cancelled")
        dialog.deleteLater()


class AttrsTreeView(TreeView):
    def __init__(self, parent):
        super(AttrsTreeView, self).__init__(parent)
        self._updateMenu()
        self._buildHandlers()
        self.packTreeView: PackTreeView = PackTreeView.instance()

    def _updateMenu(self):
        menuActions = self.attrsMenu.actions()

        self.editAct = QAction("&Edit")
        self.editAct.setStatusTip("Edit selected item")
        self.editAct.setDisabled(True)
        self.attrsMenu.insertAction(menuActions[0], self.editAct)

        self.addAct = QAction("&Add")
        self.addAct.setStatusTip("Add item to selected")
        self.addAct.setEnabled(True)
        self.attrsMenu.insertAction(self.editAct, self.addAct)

        self.addAct.triggered.connect(self._addHandler)
        self.editAct.triggered.connect(lambda: self.edit(self.currentIndex()))

        self.openInCurrTabAct = self.attrsMenu.addAction("Open in current ta&b", lambda: self.openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN), newTab=False))
        self.openInNewTabAct = self.attrsMenu.addAction("Open in new &tab", lambda: self.openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN)))
        self.openInBackgroundAct = self.attrsMenu.addAction("Open in &background tab", lambda: self.openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN), setCurrent=False))

    def _buildHandlers(self):
        self.setItemDelegate(QComboBoxEnumDelegate())
        self.clicked.connect(self.openRef)
        self.wheelClicked.connect(lambda refItem: self.openRef(refItem, newTab=True, setCurrent=False))

    def _buildHandlersForNewItem(self):
        self.model().valueChangeFailed.connect(self.parent().itemDataChangeFailed)
        self.selectionModel().currentChanged.connect(self._updateDetailInfoItemMenu)

    def _updateDetailInfoItemMenu(self, index: QModelIndex):
        if index.flags() & Qt.ItemIsEditable:
            self.editAct.setEnabled(True)
        elif index.siblingAtColumn(VALUE_COLUMN).flags() & Qt.ItemIsEditable:
            valColIndex = index.siblingAtColumn(VALUE_COLUMN)
            self.setCurrentIndex(valColIndex)
            self.editAct.setEnabled(True)
        else:
            self.editAct.setDisabled(True)

        if self.model().objByIndex(index).isLink:
            self.openInCurrTabAct.setEnabled(True)
            self.openInBackgroundAct.setEnabled(True)
            self.openInNewTabAct.setEnabled(True)
        else:
            self.openInCurrTabAct.setDisabled(True)
            self.openInBackgroundAct.setDisabled(True)
            self.openInNewTabAct.setDisabled(True)

    def _addHandler(self):
        index = self.currentIndex()
        attribute = index.data(NAME_ROLE)
        attrType = getAttrTypeHint(type(self.model().objByIndex(index).parentObj), attribute)
        self.replItemWithDialog(index, attrType, objVal=index.data(OBJECT_ROLE))

    def replItemWithDialog(self, index, objType, objVal=None):
        objName = index.data(NAME_ROLE)
        dialog = AddObjDialog(objType, self, rmDefParams=False, objName=objName, objVal=objVal)
        if dialog.exec_() == QDialog.Accepted:
            obj = dialog.getObj2add()
            item = self.model().replItemObj(obj, index)
            self.setFocus()
            self.setCurrentIndex(item)
        else:
            print("Item adding cancelled")
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

        attrsModel = DetailedInfoTable(mainObj=packItem.data(OBJECT_ROLE),
                                       package=packItem.data(PACKAGE_ROLE))
        self.setModel(attrsModel)
        self.setColumnWidth(ATTRIBUTE_COLUMN, ATTR_COLUMN_WIDTH)
        self.setItemDelegate(QComboBoxEnumDelegate())