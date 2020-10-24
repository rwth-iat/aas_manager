from PyQt5.QtCore import QModelIndex

from . import design

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .models import PackTreeViewItem, Package, StandardTable

from .views.tab import Tab
from .settings import *
from .util import toggleTheme


class EditorApp(QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initToolbar()
        self.switch2rightTreeSC = QShortcut(QKeySequence("Ctrl+Right"), self)
        self.switch2leftTreeSC = QShortcut(QKeySequence("Ctrl+Left"), self)

        self.packTreeViewModel = StandardTable()
        self.packTreeView.setHeaderHidden(True)
        self.packTreeView.setModel(self.packTreeViewModel)

        self.tabWidget.addTab(Tab(parent=self.tabWidget), "Welcome")

        self.buildHandlers()

    def initToolbar(self):
        self.toolBar.addAction(self.tabWidget.backAct)
        self.toolBar.addAction(self.tabWidget.forwardAct)

    @staticmethod
    def iterItems(root):
        def recurse(parent):
            for row in range(parent.rowCount()):
                for column in range(parent.columnCount()):
                    child = parent.child(row, column)
                    yield child
                    if child.hasChildren():
                        yield from recurse(child)

        if root is not None:
            yield from recurse(root)

    def buildHandlers(self):
        self.tabWidget.currItemChanged.connect(
            self.packTreeView.setCurrentIndex)

        self.packTreeView.wheelClicked.connect(
            self.tabWidget.openItemInBackgroundTab)
        self.packTreeView.openInBackgroundTabClicked.connect(
            self.tabWidget.openItemInBackgroundTab)
        self.packTreeView.openInNewTabClicked.connect(
            self.tabWidget.openItemInNewTab)
        self.packTreeView.openInCurrTabClicked.connect(
            self.tabWidget.openItem)
        self.packTreeView.selectionModel().currentChanged.connect(
            self.tabWidget.openItem)

        self.actionLight.triggered.connect(lambda: toggleTheme("light"))
        self.actionDark.triggered.connect(lambda: toggleTheme("dark"))
        self.actionDefault.triggered.connect(lambda: toggleTheme("standard"))

        self.switch2rightTreeSC.activated.connect(self.setFocus2rightTree)
        self.switch2leftTreeSC.activated.connect(self.packTreeView.setFocus)

    def setFocus2rightTree(self):
        tab: 'Tab' = self.tabWidget.currentWidget()
        if not tab.attrsTreeView.currentIndex().isValid():
            firstItem = tab.attrsTreeView.model().index(0, 0, QModelIndex())
            tab.attrsTreeView.setCurrentIndex(firstItem)
        self.tabWidget.currentWidget().attrsTreeView.setFocus()

    def importTestPack(self, objStore):
        self.addPack("TestPackage", objStore)

    def addPack(self, name="", objStore=None):
        pack = Package(name=name, objStore=objStore)
        self.packTreeViewModel.addItem(pack)

# ToDo logs insteads of prints
