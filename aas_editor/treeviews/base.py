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
import logging
from typing import Optional, List, Any

from PyQt6.QtCore import Qt, pyqtSignal, QRect, QPoint, QAbstractItemModel, QModelIndex, QTimer
from PyQt6.QtGui import QMouseEvent, QPaintEvent, QPainter, QWheelEvent, QAction, QPalette, QColor, QClipboard, \
    QKeyEvent
from PyQt6.QtWidgets import QTreeView, QHeaderView, QWidget, QMenu, QAbstractItemView, QApplication, QDialog

import dialogs
import settings
import widgets.messsageBoxes

from aas_editor.models.search_proxy_model import SearchProxyModel
from aas_editor.settings.app_settings import *
from aas_editor.additional.classes import DictItem
from delegates import EditDelegate
from models import StandardTable
from settings import TOOLBARS_HEIGHT, COPY_ICON, SC_COPY, PASTE_ICON, SC_PASTE, CUT_ICON, SC_CUT, ADD_ICON, SC_NEW, \
    EDIT_ICON, SC_EDIT_IN_DIALOG, DEL_ICON, SC_DELETE, UPDATE_ICON, UNDO_ICON, SC_UNDO, REDO_ICON, SC_REDO, SC_COLLAPSE, \
    SC_COLLAPSE_RECURS, COLLAPSE_ALL_ICON, SC_COLLAPSE_ALL, SC_EXPAND, SC_EXPAND_RECURS, EXPAND_ALL_ICON, SC_EXPAND_ALL, \
    ZOOM_IN_ICON, SC_ZOOM_IN, ZOOM_OUT_ICON, SC_ZOOM_OUT, OBJECT_ROLE, NAME_ROLE, UNDO_ROLE, REDO_ROLE, DEFAULT_FONT, \
    MAX_FONT_SIZE, MIN_FONT_SIZE, NOT_GIVEN, UPDATE_ROLE, PARENT_OBJ_ROLE, CLEAR_ROW_ROLE, COPY_ROLE, TYPE_HINT_ROLE, \
    ADD_ITEM_ROLE, DATA_CHANGE_FAILED_ROLE
from utils.util import getDefaultVal, getReqParams4init
from utils.util_classes import ClassesInfo
from utils.util_type import isIterable, checkType, getIterItemTypeHint, isSimpleIterable, isoftype

EMPTY_VIEW_MSG = "There are no elements in this view"
EMPTY_VIEW_ICON = None

class HeaderView(QHeaderView):
    def __init__(self, orientation, parent: Optional[QWidget] = ...) -> None:
        super(HeaderView, self).__init__(orientation, parent)
        self.setSectionsMovable(True)
        self.setStretchLastSection(True)
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

    @property
    def objForPasteCheck(self):
        if self.isEmpty():
            return None
        else:
            if type(self.objects[-1]) is list:
                return self.objects[-1][0]
            return self.objects[-1]

    @property
    def objStrForPasteCheck(self):
        if self.isEmpty():
            return None
        else:
            return self.objStrings[-1]


class BasicTreeView(QTreeView):
    wheelClicked = pyqtSignal(['QModelIndex'])
    ctrlWheelScrolled = pyqtSignal(int)
    modelChanged = pyqtSignal(['QAbstractItemModel'])

    def __init__(self, parent=None, *, emptyViewMsg=EMPTY_VIEW_MSG, emptyViewIcon=EMPTY_VIEW_ICON):
        super(BasicTreeView, self).__init__(parent)
        self.emptyViewMsg = emptyViewMsg
        self.emptyViewIcon = emptyViewIcon
        self.setMouseTracking(True)

    def setModel(self, model: QtCore.QAbstractItemModel) -> None:
        super(BasicTreeView, self).setModel(model)
        self.modelChanged.emit(model)

    def setModelWithProxy(self, model: QtCore.QAbstractItemModel) -> None:
        # proxy model will always be used by setting new models
        proxyModel = SearchProxyModel()
        proxyModel.setSourceModel(model)
        self.setModel(proxyModel)

    def sourceModel(self):
        try:
            return self.model().sourceModel()
        except AttributeError:
            return self.model()

    def collapse(self, index: QtCore.QModelIndex) -> None:
        newIndex = index.siblingAtColumn(0)
        super(BasicTreeView, self).collapse(newIndex)

    def expand(self, index: QtCore.QModelIndex) -> None:
        newIndex = index.siblingAtColumn(0)
        super(BasicTreeView, self).expand(newIndex)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            self.wheelClicked.emit(self.indexAt(event.pos()))
        else:
            super(BasicTreeView, self).mouseReleaseEvent(event)

    def wheelEvent(self, a0: QWheelEvent) -> None:
        if a0.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # ctrl press + scroll
            delta = a0.angleDelta().y()
            self.ctrlWheelScrolled.emit(delta)
        else:
            super(BasicTreeView, self).wheelEvent(a0)

    def paintEvent(self, e: QPaintEvent) -> None:
        if (self.model() and self.model().rowCount()) \
                or not (self.emptyViewMsg or self.emptyViewIcon):
            super(BasicTreeView, self).paintEvent(e)
        else:
            # If no items draw a text in the center of the viewport.
            position = self.viewport().rect().center()

            if self.emptyViewMsg:
                painter = QPainter(self.viewport())
                textRect = painter.fontMetrics().boundingRect(self.emptyViewMsg)
                textRect.moveCenter(position)
                painter.drawText(textRect, Qt.AlignmentFlag.AlignCenter, self.emptyViewMsg)
                # set position for icon
                position.setY(position.y()+textRect.height()+25)

            if self.emptyViewIcon:
                iconRect = QRect(0, 0, 50, 50)
                iconRect.moveCenter(position)
                painter.drawPixmap(iconRect, self.emptyViewIcon.pixmap(QSize(50, 50)))

    def setWindowModified(self, a0: bool) -> None:
        window = self.window()
        window.setWindowModified(a0)


class TreeView(BasicTreeView):
    openInCurrTabClicked = pyqtSignal(QModelIndex)
    openInNewTabClicked = pyqtSignal(QModelIndex)
    openInBgTabClicked = pyqtSignal(QModelIndex)
    openInNewWindowClicked = pyqtSignal(QModelIndex)

    treeClipboard = TreeClipboard()

    def __init__(self, parent=None, editEnabled: bool = True, **kwargs):
        super(TreeView, self).__init__(parent, **kwargs)
        self.editEnabled = editEnabled
        self.editingActions = []
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
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

    def addEditingAction(self, action: QAction):
        self.addAction(action)
        self.editingActions.append(action)

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
        self.addEditingAction(self.pasteAct)

        self.cutAct = QAction(CUT_ICON, "Cut", self,
                              statusTip="Cut selected item",
                              shortcut=SC_CUT,
                              shortcutContext=Qt.ShortcutContext.WidgetWithChildrenShortcut,
                              triggered=lambda: self.onCut(),
                              enabled=False)
        self.addEditingAction(self.cutAct)

        self.addAct = QAction(ADD_ICON, "&Add", self,
                              statusTip="Add item to selected",
                              shortcut=SC_NEW,
                              shortcutContext=Qt.ShortcutContext.WidgetWithChildrenShortcut,
                              triggered=lambda: self.onAddAct(),
                              enabled=False)
        self.addEditingAction(self.addAct)

        self.editCreateInDialogAct = QAction("E&dit/create in dialog", self,
                                             icon=EDIT_ICON,
                                             statusTip="Edit/create selected item in dialog",
                                             shortcut=SC_EDIT_IN_DIALOG,
                                             shortcutContext=Qt.ShortcutContext.WidgetWithChildrenShortcut,
                                             triggered=lambda: self.editCreateInDialog(),
                                             enabled=False)
        self.addEditingAction(self.editCreateInDialogAct)

        self.editAct = QAction("&Edit", self,
                               statusTip="Edit selected item",
                               triggered=lambda: self.edit(self.currentIndex()),
                               enabled=False)
        self.addEditingAction(self.editAct)

        self.delClearAct = QAction(DEL_ICON, "Delete/clear", self,
                                   statusTip="Delete/clear selected item",
                                   shortcut=SC_DELETE,
                                   shortcutContext=Qt.ShortcutContext.WidgetWithChildrenShortcut,
                                   triggered=lambda: self.onDelClear(),
                                   enabled=False)
        self.addEditingAction(self.delClearAct)

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
        self.addEditingAction(self.undoAct)

        self.redoAct = QAction(REDO_ICON, "Redo", self,
                               statusTip="Redo last edit action",
                               shortcut=SC_REDO,
                               shortcutContext=Qt.ShortcutContext.WidgetWithChildrenShortcut,
                               triggered=lambda: self.onRedo(),
                               enabled=False)
        self.addEditingAction(self.redoAct)

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

        self.openInActs = [self.openInCurrTabAct, self.openInNewTabAct, self.openInBackgroundAct,
                           self.openInNewWindowAct]

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
        self.initMenuOpenIn()

    def initMenuFolding(self):
        foldingMenu = self.attrsMenu.addMenu("Folding")
        foldingMenu.addAction(self.collapseAct)
        foldingMenu.addAction(self.collapseRecAct)
        foldingMenu.addAction(self.collapseAllAct)
        foldingMenu.addAction(self.expandAct)
        foldingMenu.addAction(self.expandRecAct)
        foldingMenu.addAction(self.expandAllAct)

    def initMenuOpenIn(self):
        openInMenu = self.attrsMenu.addMenu("Open in...")
        for act in self.openInActs:
            openInMenu.addAction(act)

    def openMenu(self, point):
        self.pasteAct.setEnabled(self.isPasteOk(self.currentIndex()))
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
            self.updateCopyCutPasteDelActs(index)
            self.updateEditActs(index)
            self.updateAddActs(index)
        else:
            self.disableAllEditingActs()

    def disableAllEditingActs(self):
        for act in self.editingActions:
            act.setEnabled(False)

    def updateCopyCutPasteDelActs(self, index: QModelIndex):
        indexValid = index.isValid()
        self.pasteAct.setEnabled(indexValid)
        self.copyAct.setEnabled(indexValid)
        self.cutAct.setEnabled(indexValid)
        self.delClearAct.setEnabled(indexValid)

    def updateEditActs(self, index: QModelIndex):
        self.editCreateInDialogAct.setEnabled(bool(index.flags() & Qt.ItemFlag.ItemIsEditable))
        self.editAct.setEnabled(self.isEditableInsideCell(index))

    def updateAddActs(self, index: QModelIndex):
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
        indexes = self.getTopLevelSameLevelIndexes(self.selectedIndexes())
        if indexes and len(indexes) == 1:
            self.onOneItemDelClear(indexes[0])
        elif indexes:
            self.onMultipleDelClear(indexes)

    def onOneItemDelClear(self, index: QModelIndex):
        attribute = index.data(NAME_ROLE)
        try:
            parentObjType = type(index.data(PARENT_OBJ_ROLE))
            defaultVal = getDefaultVal(parentObjType, attribute)
            self._setItemData(index, defaultVal, CLEAR_ROW_ROLE)
        except (AttributeError, IndexError):
            self._setItemData(index, NOT_GIVEN, CLEAR_ROW_ROLE)

    def onMultipleDelClear(self, indexes: List[QModelIndex]):
        for index in sorted(indexes, key=lambda x: x.row(), reverse=True):  # reverse to avoid shifting rows
            self.onOneItemDelClear(index)

    def onCopy(self):
        indexes = self.selectedIndexes()
        if indexes and len(indexes) == 1:
            self.onOneItemCopy(indexes[0])
        elif indexes:
            self.onMultipleItemsCopy(indexes)

    def onOneItemCopy(self, index: QModelIndex):
        data2copy = index.data(COPY_ROLE)
        text2copy = index.data(Qt.ItemDataRole.DisplayRole)
        self.treeClipboard.clear()
        self.treeClipboard.append(data2copy, objRepr=text2copy)
        clipboard = QApplication.clipboard()
        clipboard.setText(text2copy, QClipboard.Mode.Clipboard)
        self.pasteAct.setEnabled(self.isPasteOk(index))

    def onMultipleItemsCopy(self, indexes: List[QModelIndex]):
        # Get top level indexes
        top_same_level_indexes = self.getTopLevelSameLevelIndexes(indexes)
        data2copy = [i.data(COPY_ROLE) for i in top_same_level_indexes if i.data(COPY_ROLE) is not None]
        text2copy = "\n".join([i.data(Qt.ItemDataRole.DisplayRole) for i in indexes if i.isValid()])
        self.treeClipboard.clear()
        self.treeClipboard.append(data2copy, objRepr=text2copy)
        clipboard = QApplication.clipboard()
        clipboard.setText(self.treeClipboard.objStrings[-1], QClipboard.Mode.Clipboard)

    def getTopLevelSameLevelIndexes(self, indexes):
        # Remove invalid indexes just in case
        valid_indexes = [idx for idx in indexes if idx.isValid()]

        # Remove indexes whose parent is also in the list
        top_level_candidates = []
        for idx in valid_indexes:
            if idx.parent() not in valid_indexes:
                top_level_candidates.append(idx)

        if len(valid_indexes) <= 1:
            return valid_indexes

        # Determine the common parent among remaining top-level candidates
        first_parent = top_level_candidates[0].parent()
        same_level_indexes = [idx for idx in top_level_candidates if idx.parent() == first_parent]

        return same_level_indexes

    def isPasteOk(self, index: QModelIndex) -> bool:
        if self.treeClipboard.isEmpty() or not index.isValid():
            return False

        targetTypeHint = index.data(TYPE_HINT_ROLE)
        try:
            if checkType(self.treeClipboard.objForPasteCheck, targetTypeHint):
                return True
            targetObj = index.data(OBJECT_ROLE)
            if isIterable(targetObj):
                if checkType(self.treeClipboard.objForPasteCheck, getIterItemTypeHint(targetTypeHint)):
                    return True
            if checkType(self.treeClipboard.objStrForPasteCheck, targetTypeHint):
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
        index = self.currentIndex()
        if not self.isPasteOk(index):
            return
        targetParentObj = index.parent().data(OBJECT_ROLE)
        targetObj = index.data(OBJECT_ROLE)
        targetTypeHint = index.data(TYPE_HINT_ROLE)

        objs2paste = self.treeClipboard.objects[-1]
        pasteWithDialog = False
        if not isinstance(objs2paste, list):
            reqAttrsDict = getReqParams4init(type(objs2paste), rmDefParams=True)
            objs2paste = [objs2paste]
            pasteWithDialog = bool(reqAttrsDict)

        # if no req. attrs, paste data without dialog
        # else paste data with dialog for asking to check req. attrs
        if isIterable(targetObj):
            try:
                iterItemTypehint = getIterItemTypeHint(targetTypeHint)
            except TypeError:
                iterItemTypehint = getIterItemTypeHint(type(targetObj))
            paste_was_done = False
            for obj2paste in objs2paste:
                if checkType(obj2paste, iterItemTypehint):
                    self._onPasteAdd(index, obj2paste, withDialog=pasteWithDialog)
                    paste_was_done = True
            if paste_was_done:
                return
        if isIterable(targetParentObj):
            for obj2paste in objs2paste:
                self._onPasteAdd(index.parent(), obj2paste, withDialog=pasteWithDialog)
        else:
            self._onPasteReplace(index, objs2paste[0], withDialog=pasteWithDialog)

    def _onPasteAdd(self, index, obj2paste, withDialog):
        if withDialog:
            self.addItemWithDialog(parent=index, objTypeHint=type(obj2paste), objVal=obj2paste,
                                   title=f"Paste element")
        else:
            self._setItemData(index, obj2paste, ADD_ITEM_ROLE)

    def _onPasteReplace(self, index, obj2paste, withDialog):
        if withDialog:
            self.replItemWithDialog(index=index, objTypeHint=type(obj2paste), objVal=obj2paste, title=f"Paste element")
        else:
            self._setItemData(index, obj2paste, Qt.ItemDataRole.EditRole)

    def onCut(self):
        self.onCopy()
        self.onDelClear()

    def addItemWithDialog(self, parent: QModelIndex, objTypeHint, objVal=None,
                          title="", rmDefParams=False, editDialogType=dialogs.EditObjDialog, **kwargs):
        kwargs["title"] = title if title else f"Add item to {parent.data(NAME_ROLE)}"
        kwargs["parent"] = self
        kwargs["objTypeHint"] = objTypeHint
        kwargs["objVal"] = objVal
        kwargs["rmDefParams"] = rmDefParams

        try:
            dialog = editDialogType(**kwargs)
        except Exception as e:
            widgets.messsageBoxes.ErrorMessageBox.withTraceback(self, str(e)).exec()
            return False

        result = False
        while not result and dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                obj = self._getObjFromDialog(dialog)
            except Exception as e:
                widgets.messsageBoxes.ErrorMessageBox.withTraceback(self, str(e)).exec()
                continue
            result = self._setItemData(parent, obj, ADD_ITEM_ROLE)
        if dialog.result() == QDialog.DialogCode.Rejected:
            print("Item adding cancelled")
        dialog.deleteLater()
        self.setFocus()
        return result

    def replItemWithDialog(self, *, index, objTypeHint=None, objVal=None, title="", rmDefParams=False,
                           editDialogType=dialogs.EditObjDialog, **kwargs):
        kwargs["title"] = title if title else f"Edit {index.data(NAME_ROLE)}"
        kwargs["parent"] = self
        kwargs["objTypeHint"] = objTypeHint
        kwargs["objVal"] = objVal
        kwargs["rmDefParams"] = rmDefParams
        try:
            dialog = editDialogType(**kwargs)
        except Exception as e:
            widgets.messsageBoxes.ErrorMessageBox.withTraceback(self, str(e)).exec()
            return False
        result = False
        while not result and dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                obj = self._getObjFromDialog(dialog)
            except Exception as e:
                widgets.messsageBoxes.ErrorMessageBox.withTraceback(self, str(e)).exec()
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
            widgets.messsageBoxes.ErrorMessageBox.withDetailedText(self, self.model().data(topLeft, DATA_CHANGE_FAILED_ROLE)).exec()

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
            widgets.messsageBoxes.ErrorMessageBox.withTraceback(self, str(e)).exec()

    def toggleFold(self, index: QModelIndex):
        index = index.siblingAtColumn(0)
        if self.isExpanded(index):
            self.collapse(index)
        else:
            self.expand(index)
