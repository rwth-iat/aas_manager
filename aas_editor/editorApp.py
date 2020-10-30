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


class EditorApp(QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initActions()
        self.initMenu()
        self.initToolbar()

        self.packTreeViewModel = PacksTable()
        self.packTreeView.setHeaderHidden(True)
        self.packTreeView.setModel(self.packTreeViewModel)

        self.tabWidget.addTab(Tab(parent=self.tabWidget), "Welcome")

        self.buildHandlers()

    # noinspection PyArgumentList
    def initActions(self):
        self.actionOpenPack = QAction("&Open...", self,
                                      shortcut=SC_OPEN,
                                      statusTip="Open AASX package",
                                      triggered=self.openPack,
                                      enabled=True)

        self.switch2rightTreeSC = QShortcut(SC_FOCUS2RIGTH_TREE, self,
                                            activated=self.setFocus2rightTree)
        self.switch2leftTreeSC = QShortcut(SC_FOCUS2LEFT_TREE, self,
                                           activated=self.packTreeView.setFocus)
        # Theme actions
        self.actionLight = QAction("Light", self,
                                   statusTip="Choose light theme",
                                   triggered=lambda: toggleTheme("light"),
                                   enabled=True)
        self.actionDark = QAction("Dark", self,
                                  statusTip="Choose dark theme",
                                  triggered=lambda: toggleTheme("dark"),
                                  enabled=True)
        self.actionDefault = QAction("Standard", self,
                                     statusTip="Choose standard theme",
                                     triggered=lambda: toggleTheme("standard"),
                                     enabled=True)

    def initMenu(self):
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 1194, 22))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        self.menuFile = QMenu("&File", self.menubar)
        self.menuFile.addAction(self.actionOpenPack)

        self.menuView = QMenu("&View", self.menubar)
        self.menuChoose_theme = QMenu("Choose theme", self.menuView)
        self.menuChoose_theme.addAction(self.actionLight)
        self.menuChoose_theme.addAction(self.actionDark)
        self.menuChoose_theme.addAction(self.actionDefault)
        self.menuView.addAction(self.menuChoose_theme.menuAction())

        self.menuNavigate = QMenu("&Navigate", self.menubar)
        self.menuNavigate.addAction(self.tabWidget.backAct)
        self.menuNavigate.addAction(self.tabWidget.forwardAct)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuNavigate.menuAction())

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

    def openPack(self):
        packFile = QFileDialog.getOpenFileName(self, "Open AAS file",
                                               filter="AAS files (*.aasx *.xml *.json);;"
                                                      "AASX (*.aasx);; "
                                                      "XML (*.xml);;"
                                                      "JSON (*.json);; All files (*.*)",
                                               options=QFileDialog.DontResolveSymlinks |
                                                       QFileDialog.DontUseNativeDialog)
        file = packFile[0]
        if file:
            try:
                pack = Package(file)
            except (TypeError, ValueError) as e:
                QMessageBox.critical(self, "Error",
                                     f"Package {file} couldn't be opened: {e}")
            else:
                if Path(file).absolute() in self.packTreeViewModel.openedFiles():
                    QMessageBox.critical(self, "Error", f"Package {file} is already opened")
                else:
                    self.packTreeViewModel.addItem(pack)

# ToDo logs insteads of prints
