from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt, QModelIndex
from PyQt5.QtGui import QMouseEvent, QKeyEvent, QClipboard, QWheelEvent
from PyQt5.QtWidgets import QTreeView, QAction, QMenu, QApplication, QDialog, QAbstractItemView

from aas_editor.dialogs import AddObjDialog
from aas_editor.models.search_proxy_model import SearchProxyModel
from aas_editor.settings import *
from aas_editor.util import getDefaultVal, isIterable, getReqParams4init, delAASParents
import qtawesome as qta

from aas_editor.util_classes import DictItem


class TreeView(QTreeView):
    wheelClicked = pyqtSignal(['QModelIndex'])
    openInCurrTabClicked = pyqtSignal(['QModelIndex'])
    openInNewTabClicked = pyqtSignal(['QModelIndex'])
    openInBgTabClicked = pyqtSignal(['QModelIndex'])
    openInNewWindowClicked = pyqtSignal(['QModelIndex'])

    modelChanged = pyqtSignal(['QAbstractItemModel'])

    treeObjClipboard = []

    def __init__(self, parent=None):
        super(TreeView, self).__init__(parent)
        self.initActions()
        self.initMenu()
        self.setUniformRowHeights(True)
        self.buildHandlers()

    def buildHandlers(self):
        self.customContextMenuRequested.connect(self.openMenu)
        self.modelChanged.connect(self.buildNewModelHandlers)

    def buildNewModelHandlers(self, model):
        model.rowsInserted.connect(lambda parent, first, last:
                                   self.setCurrentIndex(parent.child(last, 0)))
        self.selectionModel().currentChanged.connect(self.updateMenu)

    def updateMenu(self, index: QModelIndex):
        pass

    def setModel(self, model: QtCore.QAbstractItemModel) -> None:
        super(TreeView, self).setModel(model)
        self.modelChanged.emit(model)

    def setModelWithProxy(self, model: QtCore.QAbstractItemModel) -> None:
        # proxy model will always be used by setting new models
        proxyModel = SearchProxyModel()
        proxyModel.setSourceModel(model)
        self.setModel(proxyModel)

    # noinspection PyArgumentList
    def initActions(self):
        self.copyAct = QAction(COPY_ICON, "Copy", self,
                               statusTip="Copy selected item",
                               shortcut=SC_COPY,
                               shortcutContext=Qt.WidgetWithChildrenShortcut,
                               triggered=self._copyHandler,
                               enabled=True)
        self.addAction(self.copyAct)

        self.pasteAct = QAction(PASTE_ICON, "Paste", self,
                                statusTip="Paste from clipboard",
                                shortcut=SC_PASTE,
                                shortcutContext=Qt.WidgetWithChildrenShortcut,
                                triggered=self._pasteHandler,
                                enabled=True)
        self.addAction(self.pasteAct)

        self.cutAct = QAction(CUT_ICON, "Cut", self,
                              statusTip="Cut selected item",
                              shortcut=SC_CUT,
                              shortcutContext=Qt.WidgetWithChildrenShortcut,
                              triggered=self._cutHandler,
                              enabled=True)
        self.addAction(self.cutAct)

        self.addAct = QAction(ADD_ICON, "&Add", self,
                              statusTip="Add item to selected",
                              shortcut=SC_NEW,
                              shortcutContext=Qt.WidgetWithChildrenShortcut,
                              triggered=self._addHandler,
                              enabled=False)
        self.addAction(self.addAct)

        self.delClearAct = QAction(DEL_ICON, "Delete/clear", self,
                                   statusTip="Delete/clear selected item",
                                   shortcut=SC_DELETE,
                                   shortcutContext=Qt.WidgetWithChildrenShortcut,
                                   triggered=self._delClearHandler,
                                   enabled=True)
        self.addAction(self.delClearAct)

        self.collapseAct = QAction("Collapse", self,
                                   statusTip="Collapse selected item",
                                   shortcutContext=Qt.WidgetWithChildrenShortcut,
                                   triggered=lambda: self.collapse(self.currentIndex()))
        self.addAction(self.collapseAct)

        self.collapseRecAct = QAction("Collapse recursively", self,
                                      shortcut=SC_COLLAPSE_RECURS,
                                      shortcutContext=Qt.WidgetWithChildrenShortcut,
                                      statusTip="Collapse recursively selected item",
                                      triggered=lambda: self.collapse(self.currentIndex()))
        self.addAction(self.collapseRecAct)

        self.collapseAllAct = QAction("Collapse all", self,
                                      shortcut=SC_COLLAPSE_ALL,
                                      shortcutContext=Qt.WidgetWithChildrenShortcut,
                                      statusTip="Collapse all items",
                                      triggered=self.collapseAll)
        self.addAction(self.collapseAllAct)

        self.expandAct = QAction("Expand", self,
                                 statusTip="Expand selected item",
                                 shortcutContext=Qt.WidgetWithChildrenShortcut,
                                 triggered=lambda: self.expand(self.currentIndex()))
        self.addAction(self.expandAct)

        self.expandRecAct = QAction("Expand recursively", self,
                                    shortcut=SC_EXPAND_RECURS,
                                    shortcutContext=Qt.WidgetWithChildrenShortcut,
                                    statusTip="Expand recursively selected item",
                                    triggered=lambda: self.expandRecursively(self.currentIndex()))
        self.addAction(self.expandRecAct)

        self.expandAllAct = QAction("Expand all", self,
                                    shortcut=SC_EXPAND_ALL,
                                    shortcutContext=Qt.WidgetWithChildrenShortcut,
                                    statusTip="Expand all items",
                                    triggered=self.expandAll)
        self.addAction(self.expandAllAct)

        self.openInCurrTabAct = QAction("Open in current ta&b", self,
                                        statusTip="Open selected item in current tab",
                                        enabled=False)

        self.openInNewTabAct = QAction("Open in new &tab", self,
                                       statusTip="Open selected item in new tab",
                                       enabled=False)

        self.openInBackgroundAct = QAction("Open in &background tab", self,
                                           statusTip="Open selected item in background tab",
                                           enabled=False)

        self.openInNewWindowAct = QAction("Open in new window", self,
                                          statusTip="Open selected item in new window",
                                          enabled=False)

        self.zoomInAct = QAction(qta.icon("mdi.magnify-plus"), "Zoom in", self,
                                 shortcut=SC_ZOOM_IN,
                                 shortcutContext=Qt.WidgetShortcut,
                                 statusTip="Zoom in",
                                 triggered=self.zoomIn)
        self.addAction(self.zoomInAct)

        self.zoomOutAct = QAction(ZOOM_OUT_ICON, "Zoom out", self,
                                  shortcut=SC_ZOOM_OUT,
                                  shortcutContext=Qt.WidgetShortcut,
                                  statusTip="Zoom out",
                                  triggered=self.zoomOut)
        self.addAction(self.zoomOutAct)

    def zoomIn(self):
        self.zoom(delta=+2)

    def zoomOut(self):
        self.zoom(delta=-2)

    def zoom(self, abs: int = DEFAULT_FONT.pointSize(), delta: int = 0):
        font = QFont(self.model().data(QModelIndex(), Qt.FontRole))
        if delta > 0:
            fontSize = min(font.pointSize() + 2, MAX_FONT_SIZE)
        elif delta < 0:
            fontSize = max(font.pointSize() - 2, MIN_FONT_SIZE)
        elif MIN_FONT_SIZE < abs < MAX_FONT_SIZE:
            fontSize = abs
        else:
            return
        font.setPointSize(fontSize)
        self.model().setData(QModelIndex(), font, Qt.FontRole)
        self.setFont(font)

    def initMenu(self) -> None:
        self.attrsMenu = QMenu(self)
        self.attrsMenu.addAction(self.cutAct)
        self.attrsMenu.addAction(self.copyAct)
        self.attrsMenu.addAction(self.pasteAct)
        self.attrsMenu.addSeparator()
        self.attrsMenu.addAction(self.addAct)
        self.attrsMenu.addSeparator()
        self.attrsMenu.addAction(self.delClearAct)
        self.attrsMenu.addSeparator()
        self.attrsMenu.addAction(self.zoomInAct)
        self.attrsMenu.addAction(self.zoomOutAct)
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
        self.attrsMenu.addAction(self.openInNewWindowAct)

    def openMenu(self, point):
        self.attrsMenu.exec_(self.viewport().mapToGlobal(point))

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.MiddleButton:
            self.wheelClicked.emit(self.indexAt(e.pos()))
        else:
            super(TreeView, self).mousePressEvent(e)

    def mouseDoubleClickEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.LeftButton:
            self.handleEnterEvent()
        else:
            super(TreeView, self).mouseDoubleClickEvent(e)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.state() == QAbstractItemView.EditingState:
                # if we are editing, inform base
                super(TreeView, self).keyPressEvent(event)
            else:
                self.handleEnterEvent()
        else:
            # any other key was pressed, inform base
            super(TreeView, self).keyPressEvent(event)

    def wheelEvent(self, a0: QWheelEvent) -> None:
        if a0.modifiers() & Qt.ControlModifier:
            if a0.angleDelta().y() > 0:
                self.zoomIn()
            elif a0.angleDelta().y() < 0:
                self.zoomOut()
        else:
            super(TreeView, self).wheelEvent(a0)

    def handleEnterEvent(self):
        index2edit = self.currentIndex()
        # if we're not editing, check if editable and start editing or expand/collapse
        if index2edit.flags() & Qt.ItemIsEditable:
            self.edit(index2edit)
        if index2edit.siblingAtColumn(VALUE_COLUMN).flags() & Qt.ItemIsEditable:
            if not index2edit.data(OBJECT_ROLE):
                self._editCreateHandler()
            else:
                self.edit(index2edit)
        else:
            index2fold = self.currentIndex().siblingAtColumn(0)
            if self.isExpanded(index2fold):
                self.collapse(index2fold)
            else:
                self.expand(index2fold)

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
            parentObjType = type(index.data(PARENT_OBJ_ROLE))
            defaultVal = getDefaultVal(attribute, parentObjType)
            self.model().setData(index, defaultVal, CLEAR_ROW_ROLE)
        except (AttributeError, IndexError):
            self.model().setData(index, NOT_GIVEN, CLEAR_ROW_ROLE)

    def _copyHandler(self):
        index = self.currentIndex()
        obj2copy = index.data(OBJECT_ROLE)
        delAASParents(obj2copy)  # TODO check if there is a better solution to del aas parents
        self.treeObjClipboard.clear()
        self.treeObjClipboard.append(obj2copy)
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
                self.model().setData(index.parent(), obj2paste, ADD_ITEM_ROLE)
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
                    self.model().setData(parent, DictItem(key, value), ADD_ITEM_ROLE)
            elif isIterable(obj):
                for i in obj:
                    self.model().setData(parent, i, ADD_ITEM_ROLE)
            else:
                self.model().setData(parent, obj, ADD_ITEM_ROLE)
            self.setFocus()
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
