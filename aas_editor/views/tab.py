from PyQt5.QtCore import pyqtSignal, QModelIndex, Qt
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QWidget, QLineEdit, QLabel, QMessageBox, QGridLayout, QVBoxLayout, \
    QTabWidget, QAction

from aas_editor.settings import NAME_ROLE
from aas_editor.views.treeview_detailed import AttrsTreeView
from aas_editor.util import getTreeItemPath


class TabWidget(QTabWidget):
    # signal for changing current item in packet treeview
    currItemChanged = pyqtSignal(['QModelIndex'])

    def __init__(self, parent: QWidget = None):
        super(TabWidget, self).__init__(parent)
        self.nextTabAct = QAction("Next tab", self)
        self.backAct = QAction(QIcon.fromTheme("go-previous"), "Back", self)
        self.forwardAct = QAction(QIcon.fromTheme("go-next"), "Forward", self)
        self._setupActions()
        self.buildHandlers()

    def _setupActions(self):
        self.backAct.setDisabled(True)
        self.backAct.setShortcut(QKeySequence.Back)
        self.backAct.setToolTip(f"Go back ({self.backAct.shortcut().toString()})")

        self.forwardAct.setDisabled(True)
        self.forwardAct.setShortcut(QKeySequence.Forward)
        self.forwardAct.setToolTip(f"Go forward ({self.backAct.shortcut().toString()})")

        self.nextTabAct.setShortcut(QKeySequence.NextChild)

    def buildHandlers(self):
        self.tabCloseRequested.connect(self.removeTab)
        self.currentChanged.connect(self._currentTabChanged)
        self.currItemChanged.connect(self._updateActions)
        self.backAct.triggered.connect(lambda: self.currentWidget().openPrevItem())
        self.forwardAct.triggered.connect(lambda: self.currentWidget().openNextItem())
        self.nextTabAct.triggered.connect(self._switch2nextTab)

    def tabInserted(self, index):
        super(TabWidget, self).tabInserted(index)
        tab: Tab = self.widget(index)
        tab.objectNameChanged.connect(lambda text: self.setTabText(self.indexOf(tab), text))
        tab.currItemChanged.connect(lambda packItem: self._handleCurrTabItemChanged(tab, packItem))
        tab.attrsTreeView.openInCurrTabClicked.connect(self.openItem)
        tab.attrsTreeView.openInNewTabClicked.connect(self.openItemInNewTab)
        tab.attrsTreeView.openInBackgroundTabClicked.connect(self.openItemInBackgroundTab)

    def _handleCurrTabItemChanged(self, tab, packItem):
        if tab == self.currentWidget():
            self.currItemChanged.emit(packItem)

    def _currentTabChanged(self, index):
        if index >= 0:
            self.currItemChanged.emit(self.widget(index).packItem)
        else:
            self.currItemChanged.emit(QModelIndex())

    def _switch2nextTab(self):
        nextIndex = self.currentIndex() + 1
        nextIndexPossible = (self.count() <= nextIndex)
        if nextIndexPossible:
            self.setCurrentIndex(nextIndex)
        else:
            self.setCurrentIndex(0)

    def _updateActions(self):
        tab: Tab = self.currentWidget()
        if tab:
            self.forwardAct.setEnabled(True) if tab.nextItems else self.forwardAct.setDisabled(True)
            self.backAct.setEnabled(True) if tab.prevItems else self.backAct.setDisabled(True)

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

    def openItemInBackgroundTab(self, packItem: QModelIndex) -> int:
        tab = Tab(packItem, parent=self)
        tabIndex = self.insertTab(self.currentIndex()+1, tab, tab.objectName)
        return tabIndex

    def setCurrentTab(self, tabName):
        for index in range(self.count()):
            if self.tabText(index) == tabName:
                tab = self.widget(index)
                self.setCurrentWidget(tab)
                return True
        return False

    def removeTab(self, index):
        widget = self.widget(index)
        if widget is not None:
            widget.deleteLater()
        super(TabWidget, self).removeTab(index)


class Tab(QWidget):
    currItemChanged = pyqtSignal(['QModelIndex'])

    def __init__(self, packItem=QModelIndex(), parent: TabWidget = None):
        super(Tab, self).__init__(parent)

        self.pathLine: QLineEdit = QLineEdit(self)
        self.pathLine.setReadOnly(True)

        self.descrLabel = QLabel(self)
        self.descrLabel.setWordWrap(True)
        self.descrLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.attrsTreeView = AttrsTreeView(self)

        self.packItem: QModelIndex = QModelIndex()
        self.prevItems = []
        self.nextItems = []
        self.openItem(packItem)

        self._initLayout()

    @property
    def objectName(self) -> str:
        return self.packItem.data(NAME_ROLE)

    def openItem(self, packItem):
        if not packItem == self.packItem:
            self.nextItems.clear()
            if self.packItem.isValid():
                self.prevItems.append(self.packItem)
            self._openItem(packItem)

    def openPrevItem(self):
        if self.prevItems:
            prevItem = self.prevItems.pop()
            self.nextItems.append(self.packItem)
            self._openItem(prevItem)

    def openNextItem(self):
        if self.nextItems:
            nextItem = self.nextItems.pop()
            self.prevItems.append(self.packItem)
            self._openItem(nextItem)

    def _openItem(self, packItem):
        self.packItem = packItem
        self.pathLine.setText(getTreeItemPath(packItem))
        self.descrLabel.setText("")
        self.attrsTreeView.newPackItem(packItem)
        self.attrsTreeView.selectionModel().currentChanged.connect(self.showDetailInfoItemDoc)
        self.objectNameChanged.emit(self.objectName)
        self.currItemChanged.emit(self.packItem)

    def showDetailInfoItemDoc(self, detailInfoItem: QModelIndex):
        self.descrLabel.setText(detailInfoItem.data(Qt.WhatsThisRole))

    def itemDataChangeFailed(self, msg):
        QMessageBox.critical(self, "Error", msg)

    def _initLayout(self):
        layout = QVBoxLayout(self)
        layout.setObjectName("tabLayout")
        layout.addWidget(self.pathLine)
        layout.addWidget(self.attrsTreeView)
        layout.addWidget(self.descrLabel)
        layout.setSpacing(2)
        layout.setContentsMargins(3,2,3,2)
