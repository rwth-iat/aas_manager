from typing import Iterable

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QAction, QDialog, QSizePolicy, QFrame, QAbstractScrollArea

from aas_editor.dialogs import AddObjDialog
from aas_editor.models import DetailedInfoTable
from aas_editor.qcomboboxenumdelegate import QComboBoxEnumDelegate
from aas_editor.settings import ATTR_COLUMN_WIDTH, NAME_ROLE, OBJECT_ROLE, ATTRIBUTE_COLUMN, \
    VALUE_COLUMN, NOT_GIVEN, LINKED_ITEM_ROLE, IS_LINK_ROLE
from aas_editor.util import getAttrTypeHint, getReqParams4init, isoftype, getDefaultVal, \
    isIterableType, isIterable, issubtype, getTypeHint
from aas_editor.views.treeview import TreeView


class AttrsTreeView(TreeView):
    def __init__(self, parent):
        super(AttrsTreeView, self).__init__(parent)
        self._upgradeMenu()
        self._buildHandlers()

    # noinspection PyUnresolvedReferences
    def newPackItem(self, packItem):
        self._initTreeView(packItem)
        self.model().valueChangeFailed.connect(self.parent().itemDataChangeFailed)
        self.selectionModel().currentChanged.connect(self._updateMenu)

    def _initTreeView(self, packItem):
        self.setExpandsOnDoubleClick(False)
        self.setBaseSize(QtCore.QSize(429, 555))
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.setObjectName("attrsTreeView")
        self.setModel(DetailedInfoTable(packItem))
        self.setColumnWidth(ATTRIBUTE_COLUMN, ATTR_COLUMN_WIDTH)
        self.setItemDelegate(QComboBoxEnumDelegate())

    def _buildHandlers(self):
        self.setItemDelegate(QComboBoxEnumDelegate())
        self.clicked.connect(self._openRef)
        self.wheelClicked.connect(
            lambda refItem: self._openRef(refItem, setCurrent=False))

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
            lambda: self._openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN), newTab=False))
        self.openInNewTabAct.triggered.connect(
            lambda: self._openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN)))
        self.openInBackgroundAct.triggered.connect(
            lambda: self._openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN), setCurrent=False))
        self.openInNewWindowAct.triggered.connect(
            lambda: self._openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN), newWindow=True))

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
        if self.model().objByIndex(index).isLink:
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
        attrType = getAttrTypeHint(type(self.model().objByIndex(index).parentObj), attribute)
        if objVal:
            self.addItemWithDialog(index, attrType, objVal=objVal, title=f"Add {attribute} element", rmDefParams=True)
        else:
            self.addItemWithDialog(index, attrType, title=f"Add {attribute} element", rmDefParams=True)
    # todo reimplement search func findItemByObj

    def _editCreateHandler(self, objVal=None):
        index = self.currentIndex()
        if index.isValid():
            objVal = objVal if objVal else index.data(OBJECT_ROLE)
            attribute = index.data(NAME_ROLE)
            try:
                attrType = getAttrTypeHint(type(self.model().objByIndex(index).parentObj), attribute)
            except KeyError as e:
                if objVal:
                    attrType = type(objVal)
                else:
                    raise KeyError(e)
            self.replItemWithDialog(index, attrType, title=f"Create {attribute}", objVal=objVal)

    def _openRef(self, detailInfoItem: QModelIndex, newTab=True, setCurrent=True, newWindow=False):
        if detailInfoItem.column() == VALUE_COLUMN and detailInfoItem.data(IS_LINK_ROLE):
            linkedPackItem = self.model().data(detailInfoItem, LINKED_ITEM_ROLE)
            if newWindow:
                self.openInNewWindowClicked.emit(linkedPackItem)
            elif newTab and setCurrent:
                self.openInNewTabClicked.emit(linkedPackItem)
            elif newTab and not setCurrent:
                self.openInBgTabClicked.emit(linkedPackItem)
            else:
                self.openInCurrTabClicked.emit(linkedPackItem)
