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

from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import pyqtSignal, QModelIndex, QPersistentModelIndex, QPoint, QMimeData, QUrl, \
    QStandardPaths, Qt
from PyQt5.QtGui import QIcon, QPixmap, QRegion, QDrag, QCursor, QMouseEvent, \
    QDragEnterEvent, QDragLeaveEvent, QDropEvent, QCloseEvent
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QTabWidget, QAction, QHBoxLayout, QFrame, \
    QTabBar, QMenu, QSplitter, QShortcut, QPushButton, QMessageBox, QToolButton, QFileDialog

from aas_editor.settings.app_settings import *
from aas_editor.settings.icons import FORWARD_ICON, BACK_ICON, SPLIT_VERT_ICON, SPLIT_HORIZ_ICON, ZOOM_IN_ICON, \
    ZOOM_OUT_ICON, SETTINGS_ICON
from aas_editor.settings.shortcuts import SC_BACK, SC_FORWARD, SC_SEARCH
from aas_editor.utils.util_type import getTypeName
from aas_editor.widgets import AddressLine, SearchBar, ToolBar, AttrsTreeView
from aas_editor.utils.util import getTreeItemPath
from aas_editor.widgets.lineEdit import LineEdit


class TabBar(QTabBar):
    indexTabToDrag = -1

    def __init__(self, parent=None):
        super(TabBar, self).__init__(parent)
        self.menuIndexTab = None

        self.setFixedHeight(TOOLBARS_HEIGHT)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setElideMode(Qt.ElideRight)
        self.setUsesScrollButtons(True)
        self.setTabsClosable(True)
        self.setMouseTracking(True)
        self.setMovable(True)
        self.setAcceptDrops(True)
        self.initActions()
        self.initMenu()
        self.customContextMenuRequested.connect(self.openMenu)

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        if a0.button() == Qt.RightButton:
            self.menuIndexTab = self.tabAt(a0.pos())
        super(TabBar, self).mousePressEvent(a0)

    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        if (a0.buttons() == Qt.LeftButton) and abs(a0.pos().y()) > 30:
            globalPos = self.mapToGlobal(a0.pos())
            posInTab = self.mapFromGlobal(globalPos)

            TabBar.indexTabToDrag = self.currentIndex()

            tabRect = self.tabRect(self.indexTabToDrag)
            pixmap = QPixmap(tabRect.size())
            self.render(pixmap, QPoint(), QRegion(tabRect))

            mimeData = QMimeData()
            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setPixmap(pixmap)
            cursor = QCursor(Qt.OpenHandCursor)
            drag.setHotSpot(cursor.pos())
            drag.setHotSpot(a0.pos() - posInTab)
            drag.setDragCursor(cursor.pixmap(), Qt.MoveAction)
            dropAction = drag.exec(Qt.MoveAction)
            # If the drag completed outside of the tab bar, detach the tab and move
            # the content to the current cursor position
            if dropAction == Qt.IgnoreAction:
                a0.accept()
                self.detachTab(self.indexTabToDrag, self.cursor().pos())
        else:
            super(TabBar, self).mouseMoveEvent(a0)

    def dragEnterEvent(self, a0: QDragEnterEvent) -> None:
        a0.accept()

    def dragLeaveEvent(self, a0: QDragLeaveEvent) -> None:
        a0.accept()

    def dropEvent(self, a0: QDropEvent) -> None:
        if a0.source() == self or self.indexTabToDrag < 0 or not isinstance(a0.source(), TabBar):
            a0.accept()
            return

        a0.setDropAction(Qt.MoveAction)
        a0.accept()

        insertAfter = self.tabAt(a0.pos())
        try:
            tab = a0.source().parentWidget().widget(self.indexTabToDrag)
            packItem = QModelIndex(tab.packItem)
            index=self.parentWidget().openItemInNewTab(packItem)
            a0.source().tabCloseRequested.emit(self.indexTabToDrag)
        except AttributeError as e:
            print("Error occured while drop Event:", e)
        else:
            if insertAfter and insertAfter >= 0:
                self.moveTab(index, insertAfter+1)
        TabBar.indexTabToDrag = -1

    def detachTab(self, index, point):
        # Get the tab content
        tab = self.parentWidget().widget(index)
        packItem = QModelIndex(tab.packItem)

        # Create a new detached tab window
        detachedTab = TabWidget.openItemInNewWindow(packItem)
        detachedTab.move(point)

        self.tabCloseRequested.emit(index)

    # noinspection PyArgumentList
    def initActions(self):
        self.closeAct = QAction("Close", self,
                                statusTip="Close selected tab",
                                triggered=lambda: self.tabCloseRequested.emit(self.menuIndexTab))

        self.closeOthersAct = QAction("Close others", self,
                                   statusTip="Close all tabs except selected",
                                   triggered=lambda: self.closeOthers())

        self.closeAllRightAct = QAction("Close all to the right", self,
                                        statusTip="Close all tabs to the right",
                                        triggered=lambda: self.closeAllRight())

        self.closeAllLeftAct = QAction("Close all to the left", self,
                                       statusTip="Close all tabs to the left",
                                       triggered=lambda: self.closeAllLeft())

        self.splitVerticallyAct = QAction(SPLIT_VERT_ICON,
                                          "Split vertically", self,
                                          statusTip="Split editor area into 2 tab groups",
                                          triggered=lambda: self.splitVertically())

        self.splitHorizontallyAct = QAction(SPLIT_HORIZ_ICON, "Split horizontally", self,
                                            statusTip="Split editor area into 2 tab groups",
                                            triggered=lambda: self.splitHorizontally())


    def closeOthers(self):
        for i in range(self.count()-1, -1, -1):
            if i != self.menuIndexTab:
                self.tabCloseRequested.emit(i)

    def closeAllRight(self):
        for i in range(self.count()-1, self.menuIndexTab - 1, -1):
            if i != self.menuIndexTab:
                self.tabCloseRequested.emit(i)

    def closeAllLeft(self):
        for i in range(self.menuIndexTab - 1, -1, -1):
            if i != self.menuIndexTab:
                self.tabCloseRequested.emit(i)

    def splitHorizontally(self):
        self.addTabWidget(orientation=Qt.Vertical)

    def splitVertically(self):
        self.addTabWidget(orientation=Qt.Horizontal)

    def addTabWidget(self, orientation=Qt.Horizontal):
        tabWidget: TabWidget = self.parentWidget()
        if not isinstance(tabWidget, QTabWidget):
            raise TypeError("Parent widget of Tabbar must be of type QTabWidget",
                            type(tabWidget))

        splitter: QSplitter = tabWidget.parentWidget()
        if not isinstance(splitter, QSplitter):
            raise TypeError("Parent widget of TabWidget must be of type QSplitter",
                            type(splitter))
        splitter.setOrientation(orientation)

        tab: Tab = tabWidget.widget(self.menuIndexTab)
        packItem = QModelIndex(tab.packItem)
        newTabWidget = type(tabWidget)()
        newTabWidget.openItem(packItem)

        if orientation == Qt.Horizontal:
            size = int(tabWidget.width()/2)
        else:
            size = int(tabWidget.height()/2)

        newTabWidgetIndex = splitter.indexOf(tabWidget) + 1
        sizes = splitter.sizes()
        sizes[splitter.indexOf(tabWidget)] = size
        sizes.insert(newTabWidgetIndex, size)

        splitter.insertWidget(newTabWidgetIndex, newTabWidget)
        splitter.setSizes(sizes)

    def initMenu(self) -> None:
        self.menu = QMenu(self)
        self.menu.addAction(self.closeAct)
        self.menu.addAction(self.closeOthersAct)
        self.menu.addAction(self.closeAllRightAct)
        self.menu.addAction(self.closeAllLeftAct)
        self.menu.addSeparator()
        self.menu.addAction(self.splitVerticallyAct)
        self.menu.addAction(self.splitHorizontallyAct)

    def openMenu(self, point):
        self.menu.exec_(self.mapToGlobal(point))


class Tab(QWidget):
    currItemChanged = pyqtSignal(['QModelIndex'])

    def __init__(self, packItem=QModelIndex(), parent: 'TabWidget' = None,
                 treeViewCls = AttrsTreeView, treeViewClsKwargs = None):
        super(Tab, self).__init__(parent)
        self.tabWidget = parent
        self.icon = QIcon()
        self.initActions()

        self.pathToolBar = ToolBar(self)
        self.pathToolBar.addAction(self.backAct)
        self.pathToolBar.addAction(self.forwardAct)

        self.pathWidget = QWidget(self)
        self.pathWidget.show()
        self.pathLine: AddressLine = AddressLine(self)
        self.objTypeLine = LineEdit(self, placeholderText="Object Type")
        self.objTypeLine.setFixedWidth(168)
        self.objTypeLine.setReadOnly(True)

        QWebEngineSettings.defaultSettings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.mediaWidget = QWebEngineView()
        self.saveMediaAsBtn = QPushButton(f"Save media as..", self,
                                          toolTip="Save media file as..",
                                          clicked=lambda: self.saveMediaAsWithDialog(QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)))
        self.saveMediaBtn = QPushButton(f"Save media on desktop", self,
                                        toolTip="Save media file on desktop",
                                        clicked=lambda: self.saveMediaAsWithDialog(QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)))
        self.mediaViewWidget = QWidget()
        mediaViewWidgetLayout = QVBoxLayout(self.mediaViewWidget)
        mediaViewWidgetLayout.setContentsMargins(0, 0, 0, 0)
        mediaViewWidgetLayout.addWidget(self.mediaWidget)
        mediaViewWidgetLayout.addWidget(self.saveMediaBtn)
        mediaViewWidgetLayout.addWidget(self.saveMediaAsBtn)
        self.mediaViewWidget.hide()

        self.attrsTreeView = treeViewCls(self) if not treeViewClsKwargs else treeViewCls(self, **treeViewClsKwargs)
        self.attrsTreeView.setFrameShape(QFrame.NoFrame)

        self.initToolbar()
        self.searchBar = SearchBar(self.attrsTreeView, parent=self,
                                   filterColumns=[ATTRIBUTE_COLUMN, VALUE_COLUMN], closable=True)
        self.searchBar.hide()
        self.openSearchBarSC = QShortcut(SC_SEARCH, self, activated=self.searchBar.showFocused)

        self.packItem = QPersistentModelIndex(QModelIndex())
        self.prevItems = []
        self.nextItems = []
        if packItem.isValid():
            self.openItem(packItem)
        else:
            self.openEmptyItem()

        self._initLayout()

    def initToolbar(self):
        self.toolBar = ToolBar(self)

        settingsBtn = QToolButton(icon=SETTINGS_ICON)
        settingsBtn.setPopupMode(QToolButton.InstantPopup)
        menuSettings = QMenu("Settings")
        menuSettings.addAction(QAction("Hide/show tabs bar", self,
                       statusTip="Hide/show tabs bar",
                       toggled=lambda a: self.tabWidget.tabBar().show() if a else self.tabWidget.tabBar().hide(),
                       checkable=True,
                       checked=not self.tabWidget.tabBar().isHidden()))
        menuSettings.addAction(QAction("Hide/show address line", self,
                       statusTip="Hide/show address line",
                       toggled=lambda a: self.pathWidget.show() if a else self.pathWidget.hide(),
                       checkable=True,
                       checked=not self.pathWidget.isHidden()))
        settingsBtn.setMenu(menuSettings)
        self.toolBar.addWidget(settingsBtn)

        self.toolBar.addAction(self.attrsTreeView.collapseAllAct)
        self.toolBar.addAction(self.attrsTreeView.expandAllAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.attrsTreeView.undoAct)
        self.toolBar.addAction(self.attrsTreeView.redoAct)
        self.toolBar.addAction(self.attrsTreeView.editCreateInDialogAct)
        self.toolBar.addAction(self.attrsTreeView.addAct)

    # noinspection PyArgumentList
    def initActions(self):
        self.backAct = QAction(BACK_ICON, "Back", self,
                               statusTip=f"Go back one item",
                               toolTip=f"Go back one item",
                               shortcut=SC_BACK,
                               triggered=lambda: self.openPrevItem(),
                               enabled=False)

        self.forwardAct = QAction(FORWARD_ICON, "Forward", self,
                                  statusTip=f"Go forward one item",
                                  toolTip=f"Go forward one item",
                                  shortcut=SC_FORWARD,
                                  triggered=lambda: self.openNextItem(),
                                  enabled=False)

    def windowTitle(self) -> str:
        return self.packItem.data(NAME_ROLE)

    def windowIcon(self) -> QIcon:
        return self.packItem.data(Qt.DecorationRole)

    def openItem(self, packItem: QModelIndex):
        if not packItem == QModelIndex(self.packItem):
            self.nextItems.clear()
            if self.packItem.isValid():
                self.prevItems.append(self.packItem)
            self._openItem(packItem)

    def openPrevItem(self):
        if self.prevItems:
            prevItem = self.prevItems.pop()
            self.nextItems.append(self.packItem)
            self._openItem(QModelIndex(prevItem))

    def openNextItem(self):
        if self.nextItems:
            nextItem = self.nextItems.pop()
            self.prevItems.append(self.packItem)
            self._openItem(QModelIndex(nextItem))

    def openEmptyItem(self):
        self._openItem(QModelIndex())

    def _openItem(self, packItem: QModelIndex):
        try:
            currTab: Tab = self.tabWidget.currentWidget()
            state = currTab.attrsTreeView.header().saveState()
        except AttributeError:
            # if there is no curr widget, there is no current header state, it
            state = None

        self.packItem = QPersistentModelIndex(packItem.siblingAtColumn(0))

        self.packItemObj = self.packItem.data(OBJECT_ROLE)
        self.updateMediaWidget()
        self.pathLine.setText(getTreeItemPath(self.packItem))
        self.objTypeLine.setText(getTypeName(type(self.packItemObj)))

        icon = self.packItem.data(Qt.DecorationRole)
        if icon:
            self.setWindowIcon(icon)
        self.setWindowTitle(self.packItem.data(Qt.DisplayRole))
        self.attrsTreeView.newPackItem(self.packItem)
        self.currItemChanged.emit(QModelIndex(self.packItem))

        self.forwardAct.setEnabled(True) if self.nextItems else self.forwardAct.setDisabled(True)
        self.backAct.setEnabled(True) if self.prevItems else self.backAct.setDisabled(True)
        if state:
            self.attrsTreeView.header().restoreState(state)

    def updateMediaWidget(self):
        if self.packItem.data(IS_MEDIA_ROLE):
            self.mediaWidget.setContent(b"loading...")
            self.mediaViewWidget.show()
            if not self.mediaWidget.width():
                # set equal sizes
                oldSizes = self.splitter.sizes()
                newSizes = [sum(oldSizes)/(len(oldSizes)) for size in oldSizes]
                self.splitter.setSizes(newSizes)

            try:
                mediaContent = self.packItem.data(MEDIA_CONTENT_ROLE)
                if self.packItem.data(IS_URL_MEDIA_ROLE):
                    self.mediaWidget.load(QUrl(mediaContent.value))
                else:
                    self.mediaWidget.setContent(mediaContent.value, mediaContent.mime_type)
            except Exception as e:
                logging.exception(e)
                # print(e)
                self.mediaWidget.setContent(b"Error occurred while loading media")
            self.mediaWidget.setZoomFactor(1.0)
        else:
            self.mediaViewWidget.hide()

    def saveMediaAsWithDialog(self, directory="") -> bool:
        mediaContent = self.packItem.data(MEDIA_CONTENT_ROLE)
        file = self.packItem.data(NAME_ROLE)
        saved = False
        while not saved:
            try:
                file, _ = QFileDialog.getSaveFileName(self, 'Save media File',
                                                   directory+"/"+file.strip("/"))
            except AttributeError as e:
                QMessageBox.critical(self, "Error", f"{e}")
            else:
                if file:
                    saved = self.saveMedia(mediaContent, file)
                else:
                    # cancel pressed
                    return

    def saveMedia(self, media = None, file: str = None) -> bool:
        try:
            with open(file, "wb") as f:
                f.write(media.value)
            return True
        except (TypeError, ValueError) as e:
            QMessageBox.critical(self, "Error", f"Media couldn't be saved: {file}: {e}")
        except AttributeError as e:
            QMessageBox.critical(self, "Error", f"No chosen media to save: {e}")
        return False

    def _initLayout(self):
        pathLayout = QHBoxLayout(self.pathWidget)
        pathLayout.setContentsMargins(0, 0, 0, 0)
        pathLayout.addWidget(self.pathToolBar)
        pathLayout.addWidget(self.pathLine)
        pathLayout.addWidget(self.objTypeLine)
        self.pathWidget.setFixedHeight(TOOLBARS_HEIGHT)

        toolBarWidget = QWidget()
        toolBarLayout = QHBoxLayout(toolBarWidget)
        toolBarLayout.setContentsMargins(0, 0, 0, 0)
        toolBarLayout.addWidget(self.toolBar)
        toolBarLayout.addWidget(self.searchBar)
        toolBarWidget.setFixedHeight(TOOLBARS_HEIGHT)

        treeViewWidget = QWidget()
        treeViewLayout = QVBoxLayout(treeViewWidget)
        treeViewLayout.setContentsMargins(0, 0, 0, 0)
        treeViewLayout.addWidget(self.pathWidget)
        treeViewLayout.addWidget(self.attrsTreeView)

        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setContentsMargins(0, 0, 0, 0)
        self.splitter.addWidget(treeViewWidget)
        self.splitter.addWidget(self.mediaViewWidget)

        layout = QVBoxLayout(self)
        layout.setObjectName("tabLayout")
        layout.addWidget(self.pathWidget)
        layout.addWidget(toolBarWidget)
        layout.addWidget(self.splitter)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 2, 0, 2)


class TabWidget(QTabWidget):
    # signal for changing current item in packet treeview
    currItemChanged = pyqtSignal(['QModelIndex'])
    openedTabWidgets = []

    def __init__(self, parent: QWidget = None, unclosable=False,
                 tabBarCls=TabBar, tabBarClsKwargs = None,
                 tabCls=Tab, tabClsKwargs = None):
        super(TabWidget, self).__init__(parent)
        self.unclosable = unclosable

        self.initActions()
        self.buildHandlers()

        self.setTabBar(tabBarCls(self) if not tabBarClsKwargs else tabBarCls(self, **tabBarClsKwargs))
        self.setAcceptDrops(True)
        self.setStyleSheet("QTabBar::tab { height: 25px; width: 200px}")
        self.setCurrentIndex(-1)
        self.resize(QSize(800, 500))
        TabWidget.openedTabWidgets.append(self)
        self.tabCls = tabCls
        self.tabClsKwargs = tabClsKwargs

    def closeEvent(self, a0: QCloseEvent) -> None:
        TabWidget.openedTabWidgets.remove(self)
        super(TabWidget, self).closeEvent(a0)

    # noinspection PyArgumentList
    def initActions(self):
        self.zoomInAct = QAction(ZOOM_IN_ICON, "Zoom in", self,
                                 statusTip="Zoom in detailed info",
                                 triggered=lambda: self.zoomIn())

        self.zoomOutAct = QAction(ZOOM_OUT_ICON, "Zoom out", self,
                                  statusTip="Zoom out detailed info",
                                  triggered=lambda: self.zoomOut())

    def zoomIn(self):
        if isinstance(self.currentWidget(), Tab):
            self.currentWidget().attrsTreeView.zoomIn()

    def zoomOut(self):
        if isinstance(self.currentWidget(), Tab):
            self.currentWidget().attrsTreeView.zoomOut()

    def buildHandlers(self):
        self.tabCloseRequested.connect(self.removeTab)
        self.currentChanged.connect(self.onCurrTabChanged)

    def tabInserted(self, index):
        super(TabWidget, self).tabInserted(index)
        tab: Tab = self.widget(index)
        tab.windowTitleChanged.connect(lambda text: self.setTabText(self.indexOf(tab), text))
        tab.windowIconChanged.connect(lambda icon: self.setTabIcon(self.indexOf(tab), icon))
        tab.currItemChanged.connect(lambda packItem: self.onCurrTabItemChanged(tab, packItem))
        tab.attrsTreeView.openInCurrTabClicked.connect(self.openItem)
        tab.attrsTreeView.openInNewTabClicked.connect(self.openItemInNewTab)
        tab.attrsTreeView.openInBgTabClicked.connect(self.openItemInBgTab)
        tab.attrsTreeView.openInNewWindowClicked.connect(TabWidget.openItemInNewWindow)

    def onCurrTabItemChanged(self, tab: 'Tab', packItem: QModelIndex):
        if tab == self.currentWidget():
            self.currItemChanged.emit(packItem)

    def onCurrTabChanged(self, index: int):
        if index >= 0:
            packItem = QModelIndex(self.widget(index).packItem)
            self.currItemChanged.emit(packItem)
        else:
            self.currItemChanged.emit(QModelIndex())

    def openItem(self, packItem: QModelIndex = QModelIndex()) -> int:
        if not self.count():
            return self.openItemInNewTab(packItem)
        else:
            self.currentWidget().openItem(packItem)
            return self.currentIndex()

    @classmethod
    def openItemInNewWindow(cls, packItem: QModelIndex) -> int:
        tabWindow = cls()
        tabWindow.openItemInNewTab(packItem)
        tabWindow.setWindowModality(Qt.NonModal)
        tabWindow.setWindowTitle("Tabs")
        tabWindow.show()
        return tabWindow

    def openItemInNewTab(self, packItem: QModelIndex, afterCurrent: bool = True) -> int:
        kwargs = self.tabClsKwargs if self.tabClsKwargs else {}
        tab = self.tabCls(packItem, parent=self, **kwargs)
        tabIndex = self.newTab(tab, afterCurrent)
        self.setCurrentWidget(tab)
        self.currItemChanged.emit(packItem)
        return tabIndex

    def openItemInBgTab(self, packItem: QModelIndex) -> int:
        kwargs = self.tabClsKwargs if self.tabClsKwargs else {}
        tab = self.tabCls(packItem, parent=self, **kwargs)
        tabIndex = self.newTab(tab, afterCurrent=True)
        return tabIndex

    def newTab(self, widget: QWidget, afterCurrent: bool = False) -> int:
        icon = widget.windowIcon() if widget.windowIcon() else QIcon()
        label = widget.windowTitle() if widget.windowTitle() else ""
        if afterCurrent:
            tabIndex = self.insertTab(self.currentIndex()+1, widget, icon, label)
        else:
            tabIndex = self.addTab(widget, icon, label)
        return tabIndex

    def setCurrentTab(self, tabName: str):
        for index in range(self.count()):
            if self.tabText(index) == tabName:
                tab = self.widget(index)
                self.setCurrentWidget(tab)
                return True
        return False

    def removeTab(self, index: int):
        if self.unclosable and self.count() == 1:
            return
        widget = self.widget(index)
        if widget is not None:
            widget.deleteLater()
        super(TabWidget, self).removeTab(index)
        if not self.unclosable and not self.count():
            self.deleteLater()

    def removePackTab(self, packItem: QModelIndex):
        for tabIndex in range(self.count()-1, -1, -1):
            tab: Tab = self.widget(tabIndex)
            if QModelIndex(tab.packItem).siblingAtColumn(0) == packItem.siblingAtColumn(0):
                self.removeTab(tabIndex)
