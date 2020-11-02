from pathlib import Path

from PyQt5.QtCore import QModelIndex, QRect, QStandardPaths, QSettings, QPoint, QSize
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
from .util import toggleStylesheet

import qtawesome as qta
qta.set_defaults(**ICON_DEFAULTS)


class EditorApp(QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initActions()
        self.initMenu()
        self.initToolbar()

        self.currTheme = DEFAULT_THEME

        self.packTreeModel = PacksTable()
        self.packTreeView.setHeaderHidden(True)
        self.packTreeView.setModel(self.packTreeModel)

        self.tabWidget.addTab(Tab(parent=self.tabWidget), "Welcome")

        self.buildHandlers()
        self.readSettings()

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
        self.themeActs = []
        for theme in THEMES:
            themeAct = QAction(theme, self,
                               statusTip=f"Choose {theme} theme",
                               triggered=self.toggleThemeSlot)
            self.themeActs.append(themeAct)

    def initMenu(self):
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 1194, 22))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        self.menuFile = QMenu("&File", self.menubar)
        self.menuFile.addAction(self.packTreeView.newPackAct)
        self.menuFile.addAction(self.packTreeView.openPackAct)

        self.menuFile.addSeparator()
        for recentFileAct in self.packTreeView.recentFileActs:
            self.menuFile.addAction(recentFileAct)
        self.packTreeView.recentFilesSeparator = self.menuFile.addSeparator()
        self.packTreeView.updateRecentFileActs()

        self.menuFile.addAction(self.packTreeView.saveAct)
        self.menuFile.addAction(self.packTreeView.saveAsAct)
        self.menuFile.addAction(self.packTreeView.saveAllAct)
        self.menuFile.addAction(self.packTreeView.closeAct)
        self.menuFile.addAction(self.packTreeView.closeAllAct)
        self.menuFile.addAction(self.exitAct)

        self.menuView = QMenu("&View", self.menubar)
        self.menuChoose_theme = QMenu("Choose Theme", self.menuView)
        for themeAct in self.themeActs:
            self.menuChoose_theme.addAction(themeAct)
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
        self.tabWidget.currItemChanged.connect(self.packTreeView.setCurrentIndex)

        self.packTreeView.selectionModel().currentChanged.connect(self.tabWidget.openItem)
        self.packTreeView.wheelClicked.connect(self.tabWidget.openItemInBackgroundTab)
        self.packTreeView.openInBackgroundTabClicked.connect(self.tabWidget.openItemInBackgroundTab)
        self.packTreeView.openInNewTabClicked.connect(self.tabWidget.openItemInNewTab)
        self.packTreeView.openInCurrTabClicked.connect(self.tabWidget.openItem)

        self.packTreeModel.rowsRemoved.connect(self.tabWidget.removePackTab)

    def removeTabsOfClosedRows(self, parent: QModelIndex, first: int, last: int):
        for row in range(first, last):
            packItem = self.packTreeModel.index(row, 0, parent)
            self.tabWidget.removePackTab(packItem)

    def setFocus2rightTree(self):
        tab: 'Tab' = self.tabWidget.currentWidget()
        if not tab.attrsTreeView.currentIndex().isValid():
            firstItem = tab.attrsTreeView.model().index(0, 0, QModelIndex())
            tab.attrsTreeView.setCurrentIndex(firstItem)
        self.tabWidget.currentWidget().attrsTreeView.setFocus()

    def toggleThemeSlot(self):
        action = self.sender()
        if action:
            self.toggleTheme(action.text())

    def toggleTheme(self, theme: str) -> None:
        if theme in THEMES:
            toggleStylesheet(THEMES[theme])
            self.currTheme = theme

    def closeEvent(self, a0: QCloseEvent) -> None:
        if not self.packTreeModel.openedFiles():
            self.writeSettings()
            a0.accept()
        else:
            reply = QMessageBox.question(self, 'Window Close',
                                         'Do you want to save files before closing the window?',
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                         QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.packTreeView.saveAll()
                self.writeSettings()
                a0.accept()
            elif reply == QMessageBox.No:
                self.writeSettings()
                a0.accept()
            else:
                a0.ignore()

    def readSettings(self):
        settings = QSettings(ACPLT, APPLICATION_NAME)
        theme = settings.value('theme', DEFAULT_THEME)
        self.toggleTheme(theme)
        size = settings.value('size', QSize(1194, 624))
        self.resize(size)
        splitterSize = settings.value('leftZoneSize', QSize(250, 624))
        self.layoutWidget.resize(splitterSize)
        openedAasFiles = settings.value('openedAasFiles', set())
        for file in openedAasFiles:
            self.packTreeView.openPack(file)

    def writeSettings(self):
        settings = QSettings(ACPLT, APPLICATION_NAME)
        settings.setValue('theme', self.currTheme)
        settings.setValue('size', self.size())
        settings.setValue('leftZoneSize', self.layoutWidget.size())
        settings.setValue('openedAasFiles', self.packTreeModel.openedFiles())

# ToDo logs insteads of prints
