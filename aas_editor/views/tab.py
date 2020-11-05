from PyQt5.QtCore import pyqtSignal, QModelIndex, Qt, QPersistentModelIndex, QPoint, QMimeData
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap, QRegion, QDrag, QCursor, QMouseEvent, \
    QDragEnterEvent, QDragLeaveEvent, QDropEvent
from PyQt5.QtWidgets import QWidget, QLineEdit, QLabel, QMessageBox, QGridLayout, QVBoxLayout, \
    QTabWidget, QAction, QToolBar, QHBoxLayout, QFrame, QTabBar, QMenu, QSplitter

from aas_editor.settings import NAME_ROLE, SC_BACK, SC_FORWARD
from aas_editor.views.treeview_detailed import AttrsTreeView
from aas_editor.util import getTreeItemPath

import qtawesome as qta


class TabBar(QTabBar):
    TABINDEX = []

    def __init__(self):
        super(TabBar, self).__init__()
        self.indexTab = None

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

    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        if (a0.buttons() == Qt.LeftButton) and abs(a0.pos().y()) > 30:
            print(a0.localPos(), "loCpos"*10)
            print(a0.pos(), "pos"*10)
            globalPos = self.mapToGlobal(a0.pos())
            posInTab = self.mapFromGlobal(globalPos)

            self.indexTabToDrag = self.tabAt(a0.pos())
            print(self.indexTabToDrag, "start"*20)
            self.TABINDEX.clear()
            self.TABINDEX.append(self.indexTabToDrag)

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
        else:
            super(TabBar, self).mouseMoveEvent(a0)

    def dragEnterEvent(self, a0: QDragEnterEvent) -> None:
        a0.accept()

    def dragLeaveEvent(self, a0: QDragLeaveEvent) -> None:
        a0.accept()

    def dropEvent(self, a0: QDropEvent) -> None:
        if a0.source() == self or not isinstance(a0.source(), TabBar) or not self.TABINDEX:
            return

        a0.setDropAction(Qt.MoveAction)
        a0.accept()

        indexToInsert = self.TABINDEX.pop()
        insertAfter = self.tabAt(a0.pos())

        try:
            tab = a0.source().parentWidget().widget(indexToInsert)
            packItem = QModelIndex(tab.packItem)
            self.indexTabToDrag = self.tabAt(a0.pos())
            index=self.parentWidget().openItemInNewTab(packItem)
            a0.source().tabCloseRequested.emit(indexToInsert)
            if insertAfter and insertAfter >= 0:
                self.moveTab(index, insertAfter+1)
        except AttributeError as e:
            print("Error occured while drop Event:", e)

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        if a0.button() == Qt.RightButton:
            self.indexTab = self.tabAt(a0.pos())
        super(TabBar, self).mousePressEvent(a0)

    # noinspection PyArgumentList
    def initActions(self):
        self.closeAct = QAction("Close", self,
                                statusTip="Close selected tab",
                                triggered=lambda: self.tabCloseRequested.emit(self.indexTab))

        self.closeOthersAct = QAction("Close others", self,
                                   statusTip="Close all tabs except selected",
                                   triggered=self.closeOthers)

        self.closeAllRightAct = QAction("Close all to the right", self,
                                        statusTip="Close all tabs to the right",
                                        triggered=self.closeAllRight)

        self.closeAllLeftAct = QAction("Close all to the left", self,
                                       statusTip="Close all tabs to the left",
                                       triggered=self.closeAllLeft)

        self.splitHorizontallyAct = QAction("Split horizontally", self,
                                            statusTip="Split editor area into 2 tab groups",
                                            triggered=self.splitHorizontally)

        self.splitVerticallyAct = QAction("Split vertically", self,
                                          statusTip="Split editor area into 2 tab groups",
                                          triggered=self.splitVertically)

    def closeOthers(self):
        for i in range(self.count()-1, -1, -1):
            if i != self.indexTab:
                self.tabCloseRequested.emit(i)

    def closeAllRight(self):
        for i in range(self.count()-1, self.indexTab-1, -1):
            if i != self.indexTab:
                self.tabCloseRequested.emit(i)

    def closeAllLeft(self):
        for i in range(self.indexTab-1, -1, -1):
            if i != self.indexTab:
                self.tabCloseRequested.emit(i)

    def splitHorizontally(self):
        self.addTabWidget(orientation=Qt.Horizontal)

    def splitVertically(self):
        self.addTabWidget(orientation=Qt.Vertical)

    def addTabWidget(self, orientation=Qt.Horizontal):
        tabWidget: TabWidget = self.parentWidget()
        if not isinstance(tabWidget, QTabWidget):
            raise TypeError("Parent widget of Tabbar must be of type QTabWidget",
                            type(tabWidget))

        splitter: QSplitter = tabWidget.parentWidget()
        splitter.setOrientation(orientation)
        if not isinstance(splitter, QSplitter):
            raise TypeError("Parent widget of TabWidget must be of tyep QSplitter",
                            type(splitter))

        tab: Tab = tabWidget.widget(self.indexTab)
        packItem = QModelIndex(tab.packItem)
        newTabWidget = TabWidget(splitter)
        newTabWidget.openItem(packItem)

    def initMenu(self) -> None:
        self.menu = QMenu(self)
        self.menu.addAction(self.closeAct)
        self.menu.addAction(self.closeOthersAct)
        self.menu.addAction(self.closeAllRightAct)
        self.menu.addAction(self.closeAllLeftAct)
        self.menu.addSeparator()
        self.menu.addAction(self.splitHorizontallyAct)
        self.menu.addAction(self.splitVerticallyAct)

    def openMenu(self, point):
        self.menu.exec_(self.mapToGlobal(point))

class TabWidget(QTabWidget):
    # signal for changing current item in packet treeview
    currItemChanged = pyqtSignal(['QModelIndex'])

    def __init__(self, parent: QWidget = None):
        super(TabWidget, self).__init__(parent)
        self.initActions()
        self.buildHandlers()

        self.setTabBar(TabBar())
        self.setAcceptDrops(True)
        self.indexTabToDrag = None
        self.setStyleSheet("QTabBar::tab { height: 25px; width: 200px}")
        self.setCurrentIndex(-1)

    # noinspection PyArgumentList
    def initActions(self):
        self.zoomInAct = QAction(qta.icon("mdi.magnify-minus"), "Zoom in", self,
                                 statusTip="Zoom in detailed info",
                                 triggered=self.zoomIn)

        self.zoomOutAct = QAction(qta.icon("mdi.magnify-minus"), "Zoom out", self,
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
        self.currentChanged.connect(self._currentTabChanged)

    def tabInserted(self, index):
        super(TabWidget, self).tabInserted(index)
        tab: Tab = self.widget(index)
        tab.objectNameChanged.connect(lambda text: self.setTabText(self.indexOf(tab), text))
        tab.currItemChanged.connect(lambda packItem: self._handleCurrTabItemChanged(tab, packItem))
        tab.attrsTreeView.openInCurrTabClicked.connect(self.openItem)
        tab.attrsTreeView.openInNewTabClicked.connect(self.openItemInNewTab)
        tab.attrsTreeView.openInBgTabClicked.connect(self.openItemInBgTab)

    def _handleCurrTabItemChanged(self, tab: 'Tab', packItem: QModelIndex):
        if tab == self.currentWidget():
            self.currItemChanged.emit(packItem)

    def _currentTabChanged(self, index: int):
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

    def openItemInNewTab(self, packItem: QModelIndex, afterCurrent: bool = True) -> int:
        tab = Tab(packItem, parent=self)
        if afterCurrent:
            tabIndex = self.insertTab(self.currentIndex()+1, tab, tab.objectName)
        else:
            tabIndex = self.addTab(tab, tab.objectName)
        self.setCurrentWidget(tab)
        self.currItemChanged.emit(packItem)
        return tabIndex

    def openItemInBgTab(self, packItem: QModelIndex) -> int:
        tab = Tab(packItem, parent=self)
        tabIndex = self.insertTab(self.currentIndex()+1, tab, tab.objectName)
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

    def removePackTab(self, packItem: QModelIndex):
        for tabIndex in range(self.count()-1, -1, -1):
            tab: Tab = self.widget(tabIndex)
            if QModelIndex(tab.packItem).siblingAtColumn(0) == packItem.siblingAtColumn(0):
                self.removeTab(tabIndex)

    # def mouseMoveEvent(self, a0: QMouseEvent) -> None:
    #     if a0.buttons() != Qt.RightButton:
    #         return
    #
    #     globalPos = self.mapToGlobal(a0.pos())
    #     tabBar = self.tabBar()
    #     posInTab = tabBar.mapFromGlobal(globalPos)
    #
    #     self.indexTabToDrag = tabBar.tabAt(a0.pos())
    #     tabRect = tabBar.tabRect(self.indexTabToDrag)
    #     pixmap = QPixmap(tabRect.size())
    #     tabBar.render(pixmap, QPoint(), QRegion(tabRect))
    #
    #     mimeData = QMimeData()
    #     drag = QDrag(tabBar)
    #     drag.setMimeData(mimeData)
    #     drag.setPixmap(pixmap)
    #     cursor = QCursor(Qt.OpenHandCursor)
    #     drag.setHotSpot(cursor.pos())
    #     drag.setHotSpot(a0.pos() - posInTab)
    #     drag.setDragCursor(cursor.pixmap(), Qt.MoveAction)
    #     dropAction = drag.exec(Qt.MoveAction)
    #
    # def dragEnterEvent(self, a0: QDragEnterEvent) -> None:
    #     a0.accept()
    #     if a0.source().parentWidget() != self:
    #         return
    #     self.parent().tabIndexToDrag = self.indexOf(self.widget(self.indexTabToDrag))
    #
    # def dragLeaveEvent(self, a0: QDragLeaveEvent) -> None:
    #     a0.accept()
    #
    # def dropEvent(self, a0: QDropEvent) -> None:
    #     if a0.source().parentWidget() == self:
    #         return
    #
    #     a0.setDropAction(Qt.MoveAction)
    #     a0.accept()
    #
    #     tabs = self.count()
    #
    #     tab = a0.source().parentWidget().widget(self.parent().tabIndexToDrag)
    #     if tabs == 0:
    #         self.addTab(tab, tab.objectName)
    #     else:
    #         self.insertTab(tabs+1, tab, tab.objectName)

class Tab(QWidget):
    currItemChanged = pyqtSignal(['QModelIndex'])

    def __init__(self, packItem=QModelIndex(), parent: TabWidget = None):
        super(Tab, self).__init__(parent)
        self.initActions()

        self.toolBar = QToolBar(self)
        self.toolBar.setMaximumHeight(30)
        self.toolBar.addAction(self.backAct)
        self.toolBar.addAction(self.forwardAct)

        self.pathLine: QLineEdit = QLineEdit(self)
        self.pathLine.setReadOnly(True)

        self.descrLabel = QLabel(self)
        self.descrLabel.setWordWrap(True)
        self.descrLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.attrsTreeView = AttrsTreeView(self)
        self.attrsTreeView.setFrameShape(QFrame.NoFrame)

        self.packItem = QPersistentModelIndex(QModelIndex())
        self.prevItems = []
        self.nextItems = []
        self.openItem(packItem)

        self._initLayout()

    # noinspection PyArgumentList
    def initActions(self):
        self.backAct = QAction(qta.icon("fa5s.arrow-circle-left"), "Back", self,
                               statusTip=f"Go back one item",
                               toolTip=f"Go back one item",
                               shortcut=SC_BACK,
                               triggered=self.openPrevItem,
                               enabled=False)

        self.forwardAct = QAction(qta.icon("fa5s.arrow-circle-right"), "Forward", self,
                                  statusTip=f"Go forward one item",
                                  toolTip=f"Go forward one item",
                                  shortcut=SC_FORWARD,
                                  triggered=self.openNextItem,
                                  enabled=False)

    @property
    def objectName(self) -> str:
        return self.packItem.data(NAME_ROLE)

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
        self.packItem = QPersistentModelIndex(packItem)
        self.pathLine.setText(getTreeItemPath(packItem))
        self.descrLabel.setText("")
        self.attrsTreeView.newPackItem(packItem)
        self.attrsTreeView.selectionModel().currentChanged.connect(self.showDetailInfoItemDoc)
        self.objectNameChanged.emit(self.objectName)
        self.currItemChanged.emit(QModelIndex(self.packItem))

        self.forwardAct.setEnabled(True) if self.nextItems else self.forwardAct.setDisabled(True)
        self.backAct.setEnabled(True) if self.prevItems else self.backAct.setDisabled(True)


    def showDetailInfoItemDoc(self, detailInfoItem: QModelIndex):
        self.descrLabel.setText(detailInfoItem.data(Qt.WhatsThisRole))

    def itemDataChangeFailed(self, msg):
        QMessageBox.critical(self, "Error", msg)

    def _initLayout(self):
        layout = QVBoxLayout(self)
        layout.setObjectName("tabLayout")
        pathWidget = QWidget(self)
        pathLayout = QHBoxLayout(pathWidget)
        pathLayout.setContentsMargins(0, 0, 0, 0)
        pathLayout.addWidget(self.toolBar)
        pathLayout.addWidget(self.pathLine)
        layout.addWidget(pathWidget)
        layout.addWidget(self.attrsTreeView)
        layout.addWidget(self.descrLabel)
        layout.setSpacing(2)
        layout.setContentsMargins(0,2,0,2)
