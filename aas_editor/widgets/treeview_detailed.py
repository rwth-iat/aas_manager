from typing import Iterable

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QMouseEvent, QKeyEvent
from PyQt5.QtWidgets import QAction, QAbstractScrollArea, QAbstractItemView

from aas_editor.models import DetailedInfoTable
from aas_editor.edit_delegate import EditDelegate
from aas_editor.settings import ATTR_COLUMN_WIDTH, NAME_ROLE, OBJECT_ROLE, ATTRIBUTE_COLUMN, \
    VALUE_COLUMN, LINKED_ITEM_ROLE, IS_LINK_ROLE, PARENT_OBJ_ROLE
from aas_editor.util import getAttrTypeHint, isoftype, getDefaultVal, getTypeHint
from aas_editor.widgets.treeview import TreeView


class AttrsTreeView(TreeView):
    def __init__(self, parent):
        super(AttrsTreeView, self).__init__(parent)

    # noinspection PyUnresolvedReferences
    def newPackItem(self, packItem):
        self._initTreeView(packItem)
        self.model().dataChanged.connect(self.parent().itemDataChangeFailed)

    def _initTreeView(self, packItem):
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
        self.clicked.connect(self._openRef)
        self.wheelClicked.connect(lambda refItem: self._openRef(refItem, setCurrent=False))

    # noinspection PyArgumentList
    def initMenu(self):
        super(AttrsTreeView, self).initMenu()
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
            lambda: self._openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN), newTab=False))
        self.openInNewTabAct.triggered.connect(
            lambda: self._openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN)))
        self.openInBackgroundAct.triggered.connect(
            lambda: self._openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN), setCurrent=False))
        self.openInNewWindowAct.triggered.connect(
            lambda: self._openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN), newWindow=True))

    def updateMenu(self, index: QModelIndex):
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
        if isinstance(obj, Iterable) and not isinstance(obj, (str, bytes, tuple)):
            self.addAct.setEnabled(True)
        else:
            self.addAct.setEnabled(False)

        # update paste action
        if self._isPasteOk(index):
            self.pasteAct.setEnabled(True)
        else:
            self.pasteAct.setEnabled(False)

        # update open actions
        if index.data(IS_LINK_ROLE):
            self.openInCurrTabAct.setEnabled(True)
            self.openInBackgroundAct.setEnabled(True)
            self.openInNewTabAct.setEnabled(True)
            self.openInNewWindowAct.setEnabled(True)

            self.openInCurrTabAct.setVisible(True)
            self.openInBackgroundAct.setVisible(True)
            self.openInNewTabAct.setVisible(True)
            self.openInNewWindowAct.setVisible(True)
        else:
            self.openInCurrTabAct.setEnabled(False)
            self.openInBackgroundAct.setEnabled(False)
            self.openInNewTabAct.setEnabled(False)
            self.openInNewWindowAct.setEnabled(False)

            self.openInCurrTabAct.setVisible(False)
            self.openInBackgroundAct.setVisible(False)
            self.openInNewTabAct.setVisible(False)
            self.openInNewWindowAct.setVisible(False)

    def _isPasteOk(self, index: QModelIndex) -> bool:
        if not self.treeObjClipboard:
            return False
        else:
            obj2paste = self.treeObjClipboard[0]

        attrType = getTypeHint(index)
        attrName = index.data(NAME_ROLE)

        try:
            if isoftype(obj2paste, attrType) or obj2paste == getDefaultVal(attrName, attrType):
                return True
            return False
        except AttributeError:
            return False

    def _addHandler(self, objVal=None):
        index = self.currentIndex()
        attribute = index.data(NAME_ROLE)
        attrType = getAttrTypeHint(type(index.data(PARENT_OBJ_ROLE)), attribute)
        if objVal:
            self.addItemWithDialog(index, attrType, objVal=objVal, title=f"Add {attribute} element", rmDefParams=True)
        else:
            self.addItemWithDialog(index, attrType, title=f"Add {attribute} element", rmDefParams=True)

    def _editCreateHandler(self, objVal=None):
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
                    raise KeyError(e)
            self.replItemWithDialog(index, attrType, title=f"Create {attribute}", objVal=objVal)

    def _openRef(self, detailInfoItem: QModelIndex, newTab=True, setCurrent=True, newWindow=False):
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
