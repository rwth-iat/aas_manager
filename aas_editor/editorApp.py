from pathlib import Path

from PyQt5.QtCore import QModelIndex, QRect, QStandardPaths
from aas.adapter import aasx
from aas.adapter.aasx import DictSupplementaryFileContainer

from . import design

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

from .models import Package, StandardTable, DictObjectStore
from .models.table_packs import PacksTable

from .views.tab import Tab
from .settings import *
from .util import toggleTheme

import qtawesome as qta
qta.set_defaults(**ICON_DEFAULTS)


class EditorApp(QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initActions()
        self.initMenu()
        self.initToolbar()

        self.packTreeModel = PacksTable()
        self.packTreeView.setHeaderHidden(True)
        self.packTreeView.setModel(self.packTreeModel)

        self.tabWidget.addTab(Tab(parent=self.tabWidget), "Welcome")

        self.buildHandlers()

    # noinspection PyArgumentList
    def initActions(self):
        self.exitAct = QAction(qta.icon("mdi.exit-to-app"), "E&xit", self,
                               statusTip="Exit the application",
                               triggered=self.close)

        self.switch2rightTreeSC = QShortcut(SC_FOCUS2RIGTH_TREE, self,
                                            activated=self.setFocus2rightTree)
        self.switch2leftTreeSC = QShortcut(SC_FOCUS2LEFT_TREE, self,
                                           activated=self.packTreeView.setFocus)
        # Theme actions
        self.lightThemeAct = QAction("Light", self,
                                     statusTip="Choose light theme",
                                     triggered=lambda: toggleTheme("light"),
                                     enabled=True)
        self.darkThemeAct = QAction("Dark", self,
                                    statusTip="Choose dark theme",
                                    triggered=lambda: toggleTheme("dark"),
                                    enabled=True)
        self.defaultThemeAct = QAction("Standard", self,
                                       statusTip="Choose standard theme",
                                       triggered=lambda: toggleTheme("standard"),
                                       enabled=True)

    def initMenu(self):
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 1194, 22))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        self.menuFile = QMenu("&File", self.menubar)
        self.menuFile.addAction(self.packTreeView.newPackAct)
        self.menuFile.addAction(self.packTreeView.openPackAct)
        self.menuFile.addAction(self.packTreeView.saveAct)
        self.menuFile.addAction(self.packTreeView.saveAsAct)
        self.menuFile.addAction(self.packTreeView.saveAllAct)
        self.menuFile.addAction(self.packTreeView.closeAct)
        self.menuFile.addAction(self.packTreeView.closeAllAct)
        self.menuFile.addAction(self.exitAct)

        self.menuView = QMenu("&View", self.menubar)
        self.menuChoose_theme = QMenu("Choose Theme", self.menuView)
        self.menuChoose_theme.addAction(self.lightThemeAct)
        self.menuChoose_theme.addAction(self.darkThemeAct)
        self.menuChoose_theme.addAction(self.defaultThemeAct)
        self.menuView.addAction(self.menuChoose_theme.menuAction())

        self.menuNavigate = QMenu("&Navigate", self.menubar)
        self.menuNavigate.addAction(self.tabWidget.backAct)
        self.menuNavigate.addAction(self.tabWidget.forwardAct)
        self.menuNavigate.addAction(self.packTreeView.openInNewTabAct)
        self.menuNavigate.addAction(self.packTreeView.openInCurrTabAct)
        self.menuNavigate.addAction(self.packTreeView.openInBackgroundAct)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuNavigate.menuAction())

    def initToolbar(self):
        self.toolBar.addAction(self.packTreeView.saveAct)
        self.toolBar.addAction(self.packTreeView.openPackAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.tabWidget.backAct)
        self.toolBar.addAction(self.tabWidget.forwardAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.packTreeView.addAct)

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
        self.packTreeView.selectionModel().currentChanged.connect(
            self.tabWidget.openItem)
        self.packTreeView.wheelClicked.connect(
            self.tabWidget.openItemInBackgroundTab)
        self.packTreeView.openInBackgroundTabClicked.connect(
            self.tabWidget.openItemInBackgroundTab)
        self.packTreeView.openInNewTabClicked.connect(
            self.tabWidget.openItemInNewTab)
        self.packTreeView.openInCurrTabClicked.connect(
            self.tabWidget.openItem)

    def setFocus2rightTree(self):
        tab: 'Tab' = self.tabWidget.currentWidget()
        if not tab.attrsTreeView.currentIndex().isValid():
            firstItem = tab.attrsTreeView.model().index(0, 0, QModelIndex())
            tab.attrsTreeView.setCurrentIndex(firstItem)
        self.tabWidget.currentWidget().attrsTreeView.setFocus()

# ToDo logs insteads of prints
