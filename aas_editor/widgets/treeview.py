#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
import logging
from typing import Optional, Any, List

from PyQt6.QtCore import Qt, pyqtSignal, QModelIndex, QTimer, QAbstractItemModel, QPoint
from PyQt6.QtGui import QClipboard, QPalette, QColor, QMouseEvent, QKeyEvent, QAction
from PyQt6.QtWidgets import QMenu, QApplication, QDialog, QHeaderView, QWidget, QAbstractItemView

from aas_editor.delegates import EditDelegate
from aas_editor.models import StandardTable
from aas_editor import settings
from aas_editor.settings.app_settings import *
from aas_editor.settings.icons import COPY_ICON, PASTE_ICON, CUT_ICON, ADD_ICON, DEL_ICON, UNDO_ICON, REDO_ICON, \
    ZOOM_IN_ICON, ZOOM_OUT_ICON, EXPAND_ALL_ICON, COLLAPSE_ALL_ICON, UPDATE_ICON, EDIT_ICON
from aas_editor.settings.shortcuts import SC_COPY, SC_CUT, SC_PASTE, SC_DELETE, SC_NEW, SC_REDO, SC_UNDO, SC_ZOOM_IN, \
    SC_ZOOM_OUT, SC_EXPAND_RECURS, SC_EXPAND_ALL, SC_COLLAPSE_RECURS, SC_COLLAPSE_ALL, SC_EXPAND, SC_COLLAPSE, \
    SC_EDIT_IN_DIALOG
from aas_editor.utils.util import getDefaultVal, getReqParams4init
from aas_editor.utils.util_type import checkType, isSimpleIterable, isIterable, getIterItemTypeHint, isoftype

from aas_editor.utils.util_classes import ClassesInfo
from aas_editor.additional.classes import DictItem
from aas_editor.widgets.treeview_basic import BasicTreeView
from aas_editor import dialogs


class HeaderView(QHeaderView):
    def __init__(self, orientation, parent: Optional[QWidget] = ...) -> None:
        super(HeaderView, self).__init__(orientation, parent)
        self.setSectionsMovable(True)
        self.setStretchLastSection(False)
        self.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setFixedHeight(TOOLBARS_HEIGHT)

        self.sortIndicatorChanged.connect(lambda a, b: print(a, b))
        self.currSortSection = self.sortIndicatorSection()
        self.currOrder = self.sortIndicatorOrder()

        self.sectionActions = {}
        self.initShowSectionActs()

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.initMenu()
        self.customContextMenuRequested.connect(self.openMenu)
        self.sectionClicked.connect(self.onSectionClicked)

    def openMenu(self, point: QPoint):
        self.menu.exec(self.viewport().mapToGlobal(point))

    def initMenu(self) -> None:
        self.menu = QMenu(self)
        for i in self.actions():
            self.menu.addAction(i)

    def restoreState(self, state: typing.Union[QtCore.QByteArray, bytes, bytearray]) -> bool:
        super(HeaderView, self).restoreState(state)
        self.updateMenu()

    def updateMenu(self):
        self.updateShowSectionActs()
        self.initMenu()

    def updateShowSectionActs(self):
        for action in self.actions():
            self.removeAction(action)
        self.initShowSectionActs()

    def initShowSectionActs(self):
        sections = self.count()
        for section in range(sections):
            sectionName = self.text(section)
            sectionShown = not self.isSectionHidden(section)
            act = QAction(sectionName, self,
                          toolTip=f"Show/Hide section {sectionName}",
                          statusTip=f"Show/Hide section {sectionName}",
                          checkable=True)
            act.setData(section)
            act.setChecked(sectionShown)
            act.toggled.connect(self.onToggleShowSection)
            self.addAction(act)
            self.sectionActions[section] = act

    def showAllSections(self):
        """Show all section except first"""
        for i in range(1, self.count()):
            self.showSection(i)

    def hideAllSections(self):
        """Hide all section except first"""
        for i in range(1, self.count()):
            self.hideSection(i)

    def hideSectionWithNames(self, names: typing.List[str]):
        for name in names:
            self.hideSectionWithName(name)

    def hideSectionWithName(self, name: str):
        for i in range(1, self.count()):
            if self.text(i) == name:
                self.hideSection(i)
                return True
        return False

    def showSectionWithNames(self, names: typing.List[str], only=False):
        if only:
            self.hideAllSections()
        for name in names:
            self.showSectionWithName(name)

    def showSectionWithName(self, name: str):
        for i in range(1, self.count()):
            if self.text(i) == name:
                self.showSection(i)
                return True
        return False

    def hideSection(self, alogicalIndex: int) -> None:
        super(HeaderView, self).hideSection(alogicalIndex)
        acts = self.actions()
        for act in acts:
            if act.data() == alogicalIndex:
                act.setChecked(False)
                return

    def showSection(self, alogicalIndex: int) -> None:
        super(HeaderView, self).showSection(alogicalIndex)
        acts = self.actions()
        for act in acts:
            if act.data() == alogicalIndex:
                act.setChecked(True)

    def onToggleShowSection(self, toggled):
        action: QAction = self.sender()
        section = action.data()
        if toggled:
            self.showSection(section)
        else:
            self.hideSection(section)

    def text(self, section):
        if isinstance(self.model(), QAbstractItemModel):
            return self.model().headerData(section, self.orientation())

    def onSectionClicked(self, logicalIndex: int) -> None:
        if self.currSortSection == -1 or self.currSortSection != logicalIndex:
            self.setSortIndicator(logicalIndex, Qt.SortOrder.AscendingOrder)
            self.currSortSection = logicalIndex
            self.currOrder = 0
        elif self.currOrder == 0:
            self.setSortIndicator(logicalIndex, Qt.SortOrder.DescendingOrder)
            self.currSortSection = logicalIndex
            self.currOrder = 1
        else:
            self.setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
            self.currSortSection = -1


# @dataclass
class TreeClipboard:
    def __init__(self):
        self.objects: List[Any] = []
        self.objStrings: List[str] = []

    def clear(self):
        self.objects.clear()
        self.objStrings.clear()

    def append(self, obj, objRepr: str = None):
        self.objects.append(obj)
        if objRepr is None:
            self.objStrings.append(str(obj))
        else:
            self.objStrings.append(objRepr)

    def isEmpty(self):
        if self.objects:
            return False
        else:
            return True


class TreeView(BasicTreeView):
    openInCurrTabClicked = pyqtSignal(QModelIndex)
    openInNewTabClicked = pyqtSignal(QModelIndex)
    openInBgTabClicked = pyqtSignal(QModelIndex)
    openInNewWindowClicked = pyqtSignal(QModelIndex)

    treeClipboard = TreeClipboard()

    def __init__(self, parent=None, editEnabled: bool = True, **kwargs):
        super(TreeView, self).__init__(parent, **kwargs)
        self.editEnabled = editEnabled
        self.setAlternatingRowColors(True)
        self.setAnimated(True)
        self.initActions()
        self.initMenu()
        self.setUniformRowHeights(True)
        self.buildHandlers()
        self.setItemDelegate(EditDelegate(self))  # set ColorDelegate as standard delegate
        self.setSortingEnabled(True)
        self.setHeader(HeaderView(Qt.Orientation.Horizontal, self))
        p = self.palette()
        p.setColor(QPalette.ColorRole.AlternateBase, QColor(settings.LIGHT_BLUE_ALTERNATE))
        self.setPalette(p)

    # noinspection PyArgumentList
    def initActions(self):
        self.copyAct = QAction(COPY_ICON, "Copy", self,
                               statusTip="Copy selected item",
                               shortcut=SC_COPY,
                               shortcutContext=Qt.ShortcutContext.WidgetWithChildrenShortcut,
                               triggered=lambda: self.onCopy(),
                               enabled=False)
        self.addAction(self.copyAct)

        self.pasteAct = QAction(PASTE_ICON, "Paste", self,
                                statusTip="Paste from clipboard",
                                shortcut=SC_PASTE,
                                shortcutContext=Qt.ShortcutContext.WidgetWithChildrenShortcut,
                                triggered=lambda: self.onPaste(),
                                enabled=False)
        self.addAction(self.pasteAct)

        self.cutAct = QAction(CUT_ICON, "Cut", self,
                              statusTip="Cut selected item",
                              shortcut=SC_CUT,
                              shortcutContext=Qt.ShortcutContext.WidgetWithChildrenShortcut,
                              triggered=lambda: self.onCut(),
                              enabled=False)
        self.addAction(self.cutAct)

        self.addAct = QAction(ADD_ICON, "&Add", self,
                              statusTip="Add item to selected",
                              shortcut=SC_NEW,
                              shortcutContext=Qt.ShortcutContext.WidgetWithChildrenShortcut,
                              triggered=lambda: self.onAddAct(),
                              enabled=False)
        self.addAction(self.addAct)

        self.editCreateInDialogAct = QAction("E&dit/create in dialog", self,
                                             icon=EDIT_ICON,
                                             statusTip="Edit/create selected item in dialog",
                                             shortcut=SC_EDIT_IN_DIALOG,
                                             shortcutContext=Qt.ShortcutContext.WidgetWithChildrenShortcut,
                                             triggered=lambda: self.editCreateInDialog(),
                                             enabled=False)
        self.addAction(self.editCreateInDialogAct)

        self.editAct = QAction("&Edit", self,
                               statusTip="Edit selected item",
                               triggered=lambda: self.edit(self.currentIndex()),
                               enabled=False)
        self.addAction(self.editAct)

        self.delClearAct = QAction(DEL_ICON, "Delete/clear", self,
                                   statusTip="Delete/clear selected item",
                                   shortcut=SC_DELETE,
                                   shortcutContext=Qt.ShortcutContext.WidgetWithChildrenShortcut,
                                   triggered=lambda: self.onDelClear(),
                                   enabled=False)
        self.addAction(self.delClearAct)

        self.updateAct = QAction(UPDATE_ICON, "Update/reload", self,
                                 statusTip="Update/reload selected item",
                                 shortcutContext=Qt.ShortcutContext.WidgetWithChildrenShortcut,
                                 triggered=lambda: self.onUpdate(),
                                 enabled=True)
        self.addAction(self.updateAct)

        self.undoAct = QAction(UNDO_ICON, "Undo", self,
                               statusTip="Undo last edit action",
                               shortcut=SC_UNDO,
                               shortcutContext=Qt.ShortcutContext.WidgetWithChildrenShortcut,
                               triggered=lambda: self.onUndo(),
                               enabled=False)
        self.addAction(self.undoAct)

        self.redoAct = QAction(REDO_ICON, "Redo", self,
                               statusTip="Redo last edit action",
                               shortcut=SC_REDO,
                               shortcutContext=Qt.ShortcutContext.WidgetWithChildrenShortcut,
                               triggered=lambda: self.onRedo(),
                               enabled=False)
        self.addAction(self.redoAct)

        self.collapseAct = QAction("Collapse", self,
                                   shortcut=SC_COLLAPSE,
                                   statusTip="Collapse selected item",
                                   shortcutContext=Qt.ShortcutContext.WidgetWithChildrenShortcut,
                                   triggered=lambda: self.collapse(self.currentIndex()))
        self.addAction(self.collapseAct)

        self.collapseRecAct = QAction("Collapse recursively", self,
                                      shortcut=SC_COLLAPSE_RECURS,
                                      shortcutContext=Qt.ShortcutContext.WidgetWithChildrenShortcut,
                                      statusTip="Collapse recursively selected item",
                                      triggered=lambda: self.collapse(self.currentIndex()))
        self.addAction(self.collapseRecAct)

        self.collapseAllAct = QAction(COLLAPSE_ALL_ICON, "Collapse all", self,
                                      shortcut=SC_COLLAPSE_ALL,
                                      shortcutContext=Qt.ShortcutContext.WidgetWithChildrenShortcut,
                                      statusTip="Collapse all items",
                                      triggered=lambda: self.collapseAll())
        self.addAction(self.collapseAllAct)

        self.expandAct = QAction("Expand", self,
                                 shortcut=SC_EXPAND,
                                 statusTip="Expand selected item",
                                 shortcutContext=Qt.ShortcutContext.WidgetWithChildrenShortcut,
                                 triggered=lambda: self.expand(self.currentIndex()))
        self.addAction(self.expandAct)

        self.expandRecAct = QAction("Expand recursively", self,
                                    shortcut=SC_EXPAND_RECURS,
                                    shortcutContext=Qt.ShortcutContext.WidgetWithChildrenShortcut,
                                    statusTip="Expand recursively selected item",
                                    triggered=lambda: self.expandRecursively(self.currentIndex()))
        self.addAction(self.expandRecAct)

        self.expandAllAct = QAction(EXPAND_ALL_ICON, "Expand all", self,
                                    shortcut=SC_EXPAND_ALL,
                                    shortcutContext=Qt.ShortcutContext.WidgetWithChildrenShortcut,
                                    statusTip="Expand all items",
                                    triggered=lambda: self.expandAll())
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

        self.zoomInAct = QAction(ZOOM_IN_ICON, "Zoom in", self,
                                 shortcut=SC_ZOOM_IN,
                                 shortcutContext=Qt.ShortcutContext.WidgetShortcut,
                                 statusTip="Zoom in",
                                 triggered=lambda: self.zoomIn())
        self.addAction(self.zoomInAct)

        self.zoomOutAct = QAction(ZOOM_OUT_ICON, "Zoom out", self,
                                  shortcut=SC_ZOOM_OUT,
                                  shortcutContext=Qt.ShortcutContext.WidgetShortcut,
                                  statusTip="Zoom out",
                                  triggered=lambda: self.zoomOut())
        self.addAction(self.zoomOutAct)

    def initMenu(self) -> None:
        self.attrsMenu = QMenu(self)
        self.attrsMenu.addAction(self.cutAct)
        self.attrsMenu.addAction(self.copyAct)
        self.attrsMenu.addAction(self.pasteAct)
        self.attrsMenu.addSeparator()
        self.attrsMenu.addAction(self.delClearAct)
        self.attrsMenu.addAction(self.editAct)
        self.attrsMenu.addAction(self.editCreateInDialogAct)
        self.attrsMenu.addAction(self.addAct)
        self.attrsMenu.addAction(self.updateAct)
        self.attrsMenu.addSeparator()
        self.attrsMenu.addAction(self.undoAct)
        self.attrsMenu.addAction(self.redoAct)
        self.attrsMenu.addSeparator()
        self.attrsMenu.addAction(self.zoomInAct)
        self.attrsMenu.addAction(self.zoomOutAct)
        self.attrsMenu.addSeparator()
        self.initMenuFolding()
        self.attrsMenu.addSeparator()
        self.attrsMenu.addAction(self.openInCurrTabAct)
        self.attrsMenu.addAction(self.openInNewTabAct)
        self.attrsMenu.addAction(self.openInBackgroundAct)
        self.attrsMenu.addAction(self.openInNewWindowAct)

    def initMenuFolding(self):
        foldingMenu = self.attrsMenu.addMenu("Folding")
        foldingMenu.addAction(self.collapseAct)
        foldingMenu.addAction(self.collapseRecAct)
        foldingMenu.addAction(self.collapseAllAct)
        foldingMenu.addAction(self.expandAct)
        foldingMenu.addAction(self.expandRecAct)
        foldingMenu.addAction(self.expandAllAct)

    def openMenu(self, point):
        self.attrsMenu.exec(self.viewport().mapToGlobal(point))

    def buildHandlers(self):
        self.customContextMenuRequested.connect(self.openMenu)
        self.modelChanged.connect(self.onModelChanged)
        self.ctrlWheelScrolled.connect(lambda delta: self.zoom(delta=delta))
        self.updateTreeClipboard()
        QApplication.clipboard().dataChanged.connect(self.updateTreeClipboard)

    def onModelChanged(self, model: StandardTable):
        self.selectionModel().currentChanged.connect(self.onCurrentChanged)
        self.setCurrentIndex(self.rootIndex())
        self.model().dataChanged.connect(self.onDataChanged)
        self.model().rowsInserted.connect(self.onRowsInserted)
        self.model().rowsRemoved.connect(self.onRowsRemoved)
        self.header().updateMenu()

    def onCurrentChanged(self, current: QModelIndex, previous: QModelIndex):
        self.updateActions(current)

    def onDataChanged(self, topLeft: QModelIndex, bottomRight: QModelIndex, roles):
        self.itemDataChangeFailed(topLeft, bottomRight, roles)
        # completion list will be hidden now; we will show it again after a delay
        QTimer.singleShot(100, self.updateUndoRedoActs)
        # self.setCurrentIndex(bottomRight)

    def onRowsInserted(self, parent: QModelIndex, first: int, last: int):
        index = self.model().index(last, 0, parent)
        self.setCurrentIndex(index)
        QTimer.singleShot(100, self.updateUndoRedoActs)

    def onRowsRemoved(self, parent: QModelIndex, first: int, last: int):
        self.setCurrentIndex(parent)
        QTimer.singleShot(100, self.updateUndoRedoActs)

    def updateActions(self, index: QModelIndex):
        if self.editEnabled:
            self.pasteAct.setEnabled(self.isPasteOk(index))
            self.updateCopyCutDelActs(index)
            self.updateEditActs(index)
            self.updateAddAct(index)
        else:
            self.disableAllEditingActs()

    def disableAllEditingActs(self):
        self.copyAct.setEnabled(False)
        self.cutAct.setEnabled(False)
        self.delClearAct.setEnabled(False)
        self.editCreateInDialogAct.setEnabled(False)
        self.editAct.setEnabled(False)
        self.addAct.setEnabled(False)
        self.undoAct.setEnabled(False)
        self.redoAct.setEnabled(False)

    def updateCopyCutDelActs(self, index: QModelIndex):
        if index.isValid():
            self.copyAct.setEnabled(True)
            self.cutAct.setEnabled(True)
            self.delClearAct.setEnabled(True)
        else:
            self.copyAct.setEnabled(False)
            self.cutAct.setEnabled(False)
            self.delClearAct.setEnabled(False)

    def updateEditActs(self, index: QModelIndex):
        if index.flags() & Qt.ItemFlag.ItemIsEditable:
            self.editCreateInDialogAct.setEnabled(True)
        else:
            self.editCreateInDialogAct.setEnabled(False)

        if self.isEditableInsideCell(index):
            self.editAct.setEnabled(True)
        else:
            self.editAct.setEnabled(False)

    def updateAddAct(self, index: QModelIndex):
        obj = index.data(OBJECT_ROLE)
        attrName = index.data(NAME_ROLE)

        if ClassesInfo.addActText(type(obj)):
            addActText = ClassesInfo.addActText(type(obj))
            enabled = True
        elif isIterable(obj):
            addActText = f"Add {attrName} element"
            enabled = True
        else:
            addActText = "Add"
            enabled = False
        self.addAct.setEnabled(enabled)
        self.addAct.setText(addActText)

    def updateUndoRedoActs(self):
        """update undo/redo actions"""
        # check if there is undo act
        undoEnabled = bool(self.model().data(QModelIndex(), UNDO_ROLE))
        self.undoAct.setEnabled(undoEnabled)
        # check if there is redo act
        redoEnabled = bool(self.model().data(QModelIndex(), REDO_ROLE))
        self.redoAct.setEnabled(redoEnabled)

    def zoomIn(self):
        self.zoom(delta=+2)

    def zoomOut(self):
        self.zoom(delta=-2)

    def zoom(self, pointSize: int = DEFAULT_FONT.pointSize(), delta: int = 0):
        if self.model():
            font = QFont(self.model().data(QModelIndex(), Qt.ItemDataRole.FontRole))
            if delta > 0:
                fontSize = min(font.pointSize() + 2, MAX_FONT_SIZE)
            elif delta < 0:
                fontSize = max(font.pointSize() - 2, MIN_FONT_SIZE)
            elif MIN_FONT_SIZE < pointSize < MAX_FONT_SIZE:
                fontSize = pointSize
            else:
                return
            font.setPointSize(fontSize)
            font.setItalic(False)
            self.model().setData(QModelIndex(), font, Qt.ItemDataRole.FontRole)
            self.setFont(font)
        else:
            print("zoom pressed with no model")

    def onUndo(self):
        self._setItemData(QModelIndex(), NOT_GIVEN, UNDO_ROLE)

    def onRedo(self):
        self._setItemData(QModelIndex(), NOT_GIVEN, REDO_ROLE)

    def onUpdate(self):
        index = self.currentIndex()
        self.model().setData(index, NOT_GIVEN, UPDATE_ROLE)

    def onDelClear(self):
        index = self.currentIndex()
        attribute = index.data(NAME_ROLE)
        try:
            parentObjType = type(index.data(PARENT_OBJ_ROLE))
            defaultVal = getDefaultVal(parentObjType, attribute)
            self._setItemData(index, defaultVal, CLEAR_ROW_ROLE)
        except (AttributeError, IndexError):
            self._setItemData(index, NOT_GIVEN, CLEAR_ROW_ROLE)

    def onCopy(self):
        index = self.currentIndex()
        data2copy = index.data(COPY_ROLE)
        text2copy = index.data(Qt.ItemDataRole.DisplayRole)
        self.treeClipboard.clear()
        self.treeClipboard.append(data2copy, objRepr=text2copy)
        clipboard = QApplication.clipboard()
        clipboard.setText(text2copy, QClipboard.Mode.Clipboard)
        if self.isPasteOk(index):
            self.pasteAct.setEnabled(True)
        else:
            self.pasteAct.setEnabled(False)

    def isPasteOk(self, index: QModelIndex) -> bool:
        if self.treeClipboard.isEmpty() or not index.isValid():
            return False

        obj2paste = self.treeClipboard.objects[-1]
        objStr2paste = self.treeClipboard.objStrings[-1]
        targetTypeHint = index.data(TYPE_HINT_ROLE)

        try:
            if checkType(obj2paste, targetTypeHint):
                return True
            targetObj = index.data(OBJECT_ROLE)
            if isIterable(targetObj):
                if checkType(obj2paste, getIterItemTypeHint(targetTypeHint)):
                    return True
            if checkType(objStr2paste, targetTypeHint):
                return True
        except (AttributeError, TypeError) as e:
            logging.exception(e)
        return False

    def updateTreeClipboard(self):
        txtInSystemClipboard = QApplication.clipboard().text()
        # If treeObjClipboard is empty and user have something in txtInSystemClipboard
        if not txtInSystemClipboard:
            return
        elif self.treeClipboard.isEmpty():
            self.treeClipboard.append(txtInSystemClipboard)
        # If text in clipboard and in treeObjClipboard doesn't match, last copy element is not from AASM and is actual
        elif self.treeClipboard.objStrings[-1] != txtInSystemClipboard:
            self.treeClipboard.clear()
            self.treeClipboard.append(txtInSystemClipboard)

    def onPaste(self):
        obj2paste = self.treeClipboard.objects[-1]
        index = self.currentIndex()
        targetParentObj = index.parent().data(OBJECT_ROLE)
        targetObj = index.data(OBJECT_ROLE)
        targetTypeHint = index.data(TYPE_HINT_ROLE)
        reqAttrsDict = getReqParams4init(type(obj2paste), rmDefParams=True)

        # if no req. attrs, paste data without dialog
        # else paste data with dialog for asking to check req. attrs
        if isIterable(targetObj):
            try:
                iterItemTypehint = getIterItemTypeHint(targetTypeHint)
            except TypeError:
                iterItemTypehint = getIterItemTypeHint(type(targetObj))
            if checkType(obj2paste, iterItemTypehint):
                self._onPasteAdd(index, obj2paste, withDialog=bool(reqAttrsDict))
                return
        if checkType(obj2paste, targetTypeHint):
            if isIterable(targetParentObj):
                self._onPasteAdd(index.parent(), obj2paste, withDialog=bool(reqAttrsDict))
            else:
                self._onPasteReplace(index, obj2paste, withDialog=bool(reqAttrsDict))

    def _onPasteAdd(self, index, obj2paste, withDialog):
        if withDialog:
            self.addItemWithDialog(index, type(obj2paste), objVal=obj2paste,
                                   title=f"Paste element")
        else:
            self._setItemData(index, obj2paste, ADD_ITEM_ROLE)

    def _onPasteReplace(self, index, obj2paste, withDialog):
        if withDialog:
            self.replItemWithDialog(index, type(obj2paste), objVal=obj2paste,
                                    title=f"Paste element")
        else:
            self._setItemData(index, obj2paste, Qt.ItemDataRole.EditRole)

    def onCut(self):
        self.onCopy()
        self.onDelClear()

    def addItemWithDialog(self, parent: QModelIndex, objTypeHint, objVal=None,
                          title="", rmDefParams=False, **kwargs):
        try:
            dialog = dialogs.AddObjDialog(objTypeHint, self, rmDefParams=rmDefParams,
                                          objVal=objVal, title=title, **kwargs)
        except Exception as e:
            dialogs.ErrorMessageBox.withTraceback(self, str(e)).exec()
            return False

        result = False
        while not result and dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                obj = self._getObjFromDialog(dialog)
            except Exception as e:
                dialogs.ErrorMessageBox.withTraceback(self, str(e)).exec()
                continue
            result = self._setItemData(parent, obj, ADD_ITEM_ROLE)
        if dialog.result() == QDialog.DialogCode.Rejected:
            print("Item adding cancelled")
        dialog.deleteLater()
        self.setFocus()
        return result

    def replItemWithDialog(self, index, objTypeHint, objVal=None, title="", rmDefParams=False, **kwargs):
        title = title if title else f"Edit {index.data(NAME_ROLE)}"
        try:
            dialog = dialogs.AddObjDialog(objTypeHint, self, rmDefParams=rmDefParams,
                                          objVal=objVal, title=title, **kwargs)
        except Exception as e:
            dialogs.ErrorMessageBox.withTraceback(self, str(e)).exec()
            return False
        result = False
        while not result and dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                obj = self._getObjFromDialog(dialog)
            except Exception as e:
                dialogs.ErrorMessageBox.withTraceback(self, str(e)).exec()
                continue
            result = self._setItemData(index, obj, Qt.ItemDataRole.EditRole)
        if dialog.result() == QDialog.DialogCode.Rejected:
            print("Item editing cancelled")
        dialog.deleteLater()
        self.setFocus()
        self.setCurrentIndex(index)
        return result

    def _getObjFromDialog(self, dialog):
        return dialog.getObj2add()

    def _setItemData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        if role == Qt.ItemDataRole.EditRole:
            result = self.model().setData(index, value, Qt.ItemDataRole.EditRole)
        elif role == ADD_ITEM_ROLE:
            if isinstance(value, dict):
                for key, value in value.items():
                    result = self.model().setData(index, DictItem(key, value), ADD_ITEM_ROLE)
            elif isSimpleIterable(value):
                for i in value:
                    result = self.model().setData(index, i, ADD_ITEM_ROLE)
            else:
                result = self.model().setData(index, value, ADD_ITEM_ROLE)
        elif role == CLEAR_ROW_ROLE:
            result = self.model().setData(index, value, CLEAR_ROW_ROLE)
        elif role == UNDO_ROLE:
            result = self.model().setData(index, value, UNDO_ROLE)
        elif role == REDO_ROLE:
            result = self.model().setData(index, value, REDO_ROLE)
        else:
            raise ValueError("Role can be only of Item Edit type: "
                             "EditRole, AddItemRole, CLEAR_ROLE, UNDO_ROLE, REDO_ROLE")
        self.setWindowModified(True)
        return result

    def commitData(self, editor: QWidget) -> None:
        super(TreeView, self).commitData(editor)
        self.setWindowModified(True)

    def itemDataChangeFailed(self, topLeft, bottomRight, roles):
        """Check dataChanged signal if data change failed and show Error dialog if failed"""
        if DATA_CHANGE_FAILED_ROLE in roles:
            dialogs.ErrorMessageBox.withDetailedText(self, self.model().data(topLeft, DATA_CHANGE_FAILED_ROLE)).exec()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.state() == QAbstractItemView.State.EditingState:
                # if we are editing, inform base
                super(TreeView, self).keyPressEvent(event)
            else:
                self.onEnterEvent()
        else:
            # any other key was pressed, inform base
            super(TreeView, self).keyPressEvent(event)

    def keyboardSearch(self, search: str) -> None:
        # The func fixed following error: programm crashes if you type too fast any keys!
        return None

    def keyReleaseEvent(self, event) -> None:
        if event.key() in (Qt.Key.Key_Right, Qt.Key.Key_Left):
            return
        else:
            super(TreeView, self).keyReleaseEvent(event)

    def mouseDoubleClickEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.MouseButton.LeftButton:
            self.onDoubleClickEvent()
        else:
            super(TreeView, self).mouseDoubleClickEvent(e)

    def onDoubleClickEvent(self):
        index = self.currentIndex()
        # if we're not editing, check if editable and start editing or expand/collapse
        if index.flags() & Qt.ItemFlag.ItemIsEditable:
            self.editInCellOrInDialog(index)
        else:
            self.toggleFold(index)

    def onEnterEvent(self):
        index = self.currentIndex()
        # if we're not editing, check if editable and start editing or expand/collapse
        if index.flags() & Qt.ItemFlag.ItemIsEditable:
            self.editInCellOrInDialog(index)
        else:
            self.toggleFold(index)

    def editInCellOrInDialog(self, index: QModelIndex) -> None:
        self.setCurrentIndex(index)
        # edit acts will be actually triggered only if enabled
        if self.isEditableInsideCell(index) and self.editAct.isEnabled():
            self.editAct.trigger()
        elif self.editCreateInDialogAct.isEnabled():
            self.editCreateInDialogAct.trigger()

    def isEditableInsideCell(self, index: QModelIndex):
        if index.flags() & Qt.ItemFlag.ItemIsEditable:
            data = index.data(Qt.ItemDataRole.EditRole)
            if isoftype(data, self.itemDelegate().editableTypesInTable) and data not in settings.EMPTY_VALUES:
                return True
        return False

    def editCreateInDialog(self, objVal=None, index=QModelIndex()):
        try:
            self.onEditCreate(objVal, index)
        except Exception as e:
            dialogs.ErrorMessageBox.withTraceback(self, str(e)).exec()

    def toggleFold(self, index: QModelIndex):
        index = index.siblingAtColumn(0)
        if self.isExpanded(index):
            self.collapse(index)
        else:
            self.expand(index)
