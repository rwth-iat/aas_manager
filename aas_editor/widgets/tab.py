from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import pyqtSignal, QModelIndex, QPersistentModelIndex, QPoint, QMimeData, QUrl
from PyQt5.QtGui import QIcon, QPixmap, QRegion, QDrag, QCursor, QMouseEvent, \
    QDragEnterEvent, QDragLeaveEvent, QDropEvent, QCloseEvent
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, \
    QTabWidget, QAction, QHBoxLayout, QFrame, QTabBar, QMenu, QSplitter, QShortcut
from aas.model import Blob, File

from aas_editor.package import StoredFile
from aas_editor.settings.app_settings import *
from aas_editor.widgets import AddressLine, SearchBar, ToolBar, AttrsTreeView
from aas_editor.utils.util import getTreeItemPath


class TabBar(QTabBar):
    indexTabToDrag = -1

    def __init__(self, parent=None):
        super(TabBar, self).__init__(parent)
        self.menuIndexTab = None

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
                                   triggered=self.closeOthers)

        self.closeAllRightAct = QAction("Close all to the right", self,
                                        statusTip="Close all tabs to the right",
                                        triggered=self.closeAllRight)

        self.closeAllLeftAct = QAction("Close all to the left", self,
                                       statusTip="Close all tabs to the left",
                                       triggered=self.closeAllLeft)

        self.splitVerticallyAct = QAction(SPLIT_VERT_ICON,
                                          "Split vertically", self,
                                          statusTip="Split editor area into 2 tab groups",
                                          triggered=self.splitVertically)

        self.splitHorizontallyAct = QAction(SPLIT_HORIZ_ICON, "Split horizontally", self,
                                            statusTip="Split editor area into 2 tab groups",
                                            triggered=self.splitHorizontally)


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
        newTabWidget = TabWidget()
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


class TabWidget(QTabWidget):
    # signal for changing current item in packet treeview
    currItemChanged = pyqtSignal(['QModelIndex'])
    openedTabWidgets = []

    def __init__(self, parent: QWidget = None, unclosable=False):
        super(TabWidget, self).__init__(parent)
        self.unclosable = unclosable

        self.initActions()
        self.buildHandlers()

        self.setTabBar(TabBar(self))
        self.setAcceptDrops(True)
        self.setStyleSheet("QTabBar::tab { height: 25px; width: 200px}")
        self.setCurrentIndex(-1)
        self.resize(QSize(800, 500))
        TabWidget.openedTabWidgets.append(self)

    def closeEvent(self, a0: QCloseEvent) -> None:
        TabWidget.openedTabWidgets.remove(self)
        super(TabWidget, self).closeEvent(a0)

    # noinspection PyArgumentList
    def initActions(self):
        self.zoomInAct = QAction(ZOOM_IN_ICON, "Zoom in", self,
                                 statusTip="Zoom in detailed info",
                                 triggered=self.zoomIn)

        self.zoomOutAct = QAction(ZOOM_OUT_ICON, "Zoom out", self,
                                  statusTip="Zoom out detailed info",
                                  triggered=self.zoomOut)

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

    @staticmethod
    def openItemInNewWindow(packItem: QModelIndex) -> int:
        tabWindow = TabWidget()
        tabWindow.openItemInNewTab(packItem)
        tabWindow.setWindowModality(Qt.NonModal)
        tabWindow.setWindowTitle("Tabs")
        tabWindow.show()
        return tabWindow

    def openItemInNewTab(self, packItem: QModelIndex, afterCurrent: bool = True) -> int:
        tab = Tab(packItem, parent=self)
        tabIndex = self.newTab(tab, afterCurrent)
        self.setCurrentWidget(tab)
        self.currItemChanged.emit(packItem)
        return tabIndex

    def openItemInBgTab(self, packItem: QModelIndex) -> int:
        tab = Tab(packItem, parent=self)
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


class Tab(QWidget):
    currItemChanged = pyqtSignal(['QModelIndex'])

    def __init__(self, packItem=QModelIndex(), parent: TabWidget = None):
        super(Tab, self).__init__(parent)
        self.icon = QIcon()
        self.initActions()

        self.pathToolBar = ToolBar(self)
        self.pathToolBar.addAction(self.backAct)
        self.pathToolBar.addAction(self.forwardAct)

        self.pathLine: AddressLine = AddressLine(self)

        self.descrLabel = QLabel(self)
        self.descrLabel.setWordWrap(True)
        self.descrLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)

        QWebEngineSettings.defaultSettings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.mediaWidget = QWebEngineView()
        self.mediaWidget.hide()

        self.attrsTreeView = AttrsTreeView(self)
        self.attrsTreeView.setFrameShape(QFrame.NoFrame)

        self.toolBar = ToolBar(self)
        self.toolBar.addAction(self.attrsTreeView.zoomInAct)
        self.toolBar.addAction(self.attrsTreeView.zoomOutAct)
        self.toolBar.addAction(self.attrsTreeView.collapseAllAct)
        self.toolBar.addAction(self.attrsTreeView.expandAllAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.attrsTreeView.copyAct)
        self.toolBar.addAction(self.attrsTreeView.cutAct)
        self.toolBar.addAction(self.attrsTreeView.pasteAct)
        self.toolBar.addAction(self.attrsTreeView.delClearAct)
        self.toolBar.addAction(self.attrsTreeView.editCreateInDialogAct)
        self.toolBar.addAction(self.attrsTreeView.addAct)
        self.searchBar = SearchBar(self.attrsTreeView, parent=self,
                                   filterColumns=[ATTRIBUTE_COLUMN, VALUE_COLUMN], closable=True)
        self.searchBar.hide()
        self.openSearchBarSC = QShortcut(SC_SEARCH, self, activated=self.openSearchBar)

        self.packItem = QPersistentModelIndex(QModelIndex())
        self.prevItems = []
        self.nextItems = []
        self.openItem(packItem)

        self._initLayout()

    # noinspection PyArgumentList
    def initActions(self):
        self.backAct = QAction(BACK_ICON, "Back", self,
                               statusTip=f"Go back one item",
                               toolTip=f"Go back one item",
                               shortcut=SC_BACK,
                               triggered=self.openPrevItem,
                               enabled=False)

        self.forwardAct = QAction(FORWARD_ICON, "Forward", self,
                                  statusTip=f"Go forward one item",
                                  toolTip=f"Go forward one item",
                                  shortcut=SC_FORWARD,
                                  triggered=self.openNextItem,
                                  enabled=False)

    def windowTitle(self) -> str:
        return self.packItem.data(NAME_ROLE)

    def windowIcon(self) -> QIcon:
        return self.packItem.data(Qt.DecorationRole)

    def openSearchBar(self):
        self.searchBar.show()
        self.searchBar.searchLine.setFocus()

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

    def _openItem(self, packItem: QModelIndex):
        self.packItem = QPersistentModelIndex(packItem.siblingAtColumn(0))
        self.pathLine.setText(getTreeItemPath(self.packItem))
        self.descrLabel.setText("")

        self.packItemObj = self.packItem.data(OBJECT_ROLE)
        self.updateMediaWidget()

        icon = self.packItem.data(Qt.DecorationRole)
        if icon:
            self.setWindowIcon(icon)
        self.setWindowTitle(self.packItem.data(Qt.DisplayRole))
        self.attrsTreeView.newPackItem(self.packItem)
        self.attrsTreeView.selectionModel().currentChanged.connect(self.showDetailInfoItemDoc)
        self.currItemChanged.emit(QModelIndex(self.packItem))

        self.forwardAct.setEnabled(True) if self.nextItems else self.forwardAct.setDisabled(True)
        self.backAct.setEnabled(True) if self.prevItems else self.backAct.setDisabled(True)

    def updateMediaWidget(self):
        if self.packItem.data(IS_MEDIA_ROLE):
            self.mediaWidget.setContent(b"loading...")
            self.mediaWidget.show()
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
                print(e)
                self.mediaWidget.setContent(b"Error occurred while loading media")
            self.mediaWidget.setZoomFactor(1.0)
        else:
            self.mediaWidget.hide()

    def showDetailInfoItemDoc(self, detailInfoItem: QModelIndex):
        self.descrLabel.setText(detailInfoItem.data(Qt.WhatsThisRole))

    def _initLayout(self):
        pathWidget = QWidget()
        pathLayout = QHBoxLayout(pathWidget)
        pathLayout.setContentsMargins(0, 0, 0, 0)
        pathLayout.addWidget(self.pathToolBar)
        pathLayout.addWidget(self.pathLine)
        pathWidget.setFixedHeight(TOOLBARS_HEIGHT)

        toolBarWidget = QWidget()
        toolBarLayout = QHBoxLayout(toolBarWidget)
        toolBarLayout.setContentsMargins(0, 0, 0, 0)
        toolBarLayout.addWidget(self.toolBar)
        toolBarLayout.addWidget(self.searchBar)
        toolBarWidget.setFixedHeight(TOOLBARS_HEIGHT)

        treeViewWidget = QWidget()
        treeViewLayout = QVBoxLayout(treeViewWidget)
        treeViewLayout.setContentsMargins(0, 0, 0, 0)
        treeViewLayout.addWidget(pathWidget)
        treeViewLayout.addWidget(self.attrsTreeView)
        treeViewLayout.addWidget(self.descrLabel)

        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setContentsMargins(0, 0, 0, 0)
        self.splitter.addWidget(treeViewWidget)
        self.splitter.addWidget(self.mediaWidget)

        layout = QVBoxLayout(self)
        layout.setObjectName("tabLayout")
        layout.addWidget(pathWidget)
        layout.addWidget(toolBarWidget)
        layout.addWidget(self.splitter)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 2, 0, 2)
