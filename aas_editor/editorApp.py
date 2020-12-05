from PyQt5.QtCore import Qt, QModelIndex, QSettings

from aas_editor.widgets import SearchBar, AddressLine
from . import design

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .models import DetailedInfoTable
from .models.table_packs import PacksTable

from .widgets.tab import Tab
from .settings import *
from .util import toggleStylesheet


class EditorApp(QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.currTheme = DEFAULT_THEME

        self.packTreeModel = PacksTable(COLUMNS_IN_PACKS_TABLE)
        self.packTreeView.setModelWithProxy(self.packTreeModel)
        self.packTreeView.hideColumn(VALUE_COLUMN)

        AddressLine.setModel(self.packTreeView.model())

        self.searchBarPack = SearchBar(self.packTreeView, filterColumns=[ATTRIBUTE_COLUMN],
                                       parent=self.leftLayoutWidget)
        self.leftVerticalLayout.insertWidget(1, self.searchBarPack)

        welcomeTab = self.mainTabWidget.addTab(Tab(parent=self.mainTabWidget), "Welcome")
        self.mainTabWidget.widget(welcomeTab).openSearchBar()

        self.initActions()
        self.initMenu()
        self.initToolbars()
        self.buildHandlers()
        self.readSettings()

    # noinspection PyArgumentList
    def initActions(self):
        self.exitAct = QAction(EXIT_ICON, "E&xit", self,
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
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.packTreeView.closeAct)
        self.menuFile.addAction(self.packTreeView.closeAllAct)
        self.menuFile.addAction(self.exitAct)

        self.menuView = QMenu("&View", self.menubar)
        self.menuChoose_theme = QMenu("Choose Theme", self.menuView)
        for themeAct in self.themeActs:
            self.menuChoose_theme.addAction(themeAct)
        self.menuView.addAction(self.menuChoose_theme.menuAction())
        self.menuAppearance = QMenu("Appearance", self.menuView)
        self.menuAppearance.addAction(self.toolBar.toggleViewAction())
        self.menuAppearance.addAction(self.searchBarPack.toggleViewAction())
        self.menuView.addAction(self.menuAppearance.menuAction())
        self.menuView.addSection("AAS file view")
        self.menuView.addAction(self.packTreeView.zoomInAct)
        self.menuView.addAction(self.packTreeView.zoomOutAct)
        self.menuView.addSection("Detailed view")
        self.menuView.addAction(self.mainTabWidget.zoomInAct)
        self.menuView.addAction(self.mainTabWidget.zoomOutAct)

        self.menuNavigate = QMenu("&Navigate", self.menubar)
        # self.menuNavigate.addAction(self.tabWidget.backAct)
        # self.menuNavigate.addAction(self.tabWidget.forwardAct)
        self.menuNavigate.addSeparator()
        self.menuNavigate.addAction(self.packTreeView.openInNewTabAct)
        self.menuNavigate.addAction(self.packTreeView.openInCurrTabAct)
        self.menuNavigate.addAction(self.packTreeView.openInBackgroundAct)
        self.menuNavigate.addAction(self.packTreeView.openInNewWindowAct)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuNavigate.menuAction())

    def initToolbars(self):
        self.toolBar.addAction(self.packTreeView.saveAllAct)
        self.toolBar.addAction(self.packTreeView.saveAct)
        self.toolBar.addAction(self.packTreeView.openPackAct)
        self.toolBar.addAction(self.packTreeView.newPackAct)

        settingsBtn = QToolButton(icon=SETTINGS_ICON)
        settingsBtn.setPopupMode(QToolButton.InstantPopup)
        menuSettings = QMenu("Settings")
        menuSettings.addAction(self.packTreeView.zoomInAct)
        menuSettings.addAction(self.packTreeView.zoomOutAct)
        menuSettings.addAction(self.packTreeView.autoScrollToSrcAct)
        menuSettings.addAction(self.packTreeView.autoScrollFromSrcAct)
        settingsBtn.setMenu(menuSettings)

        self.packToolBar.addWidget(settingsBtn)
        self.packToolBar.addAction(self.packTreeView.collapseAllAct)
        self.packToolBar.addAction(self.packTreeView.expandAllAct)
        self.packToolBar.addSeparator()
        self.packToolBar.addAction(self.packTreeView.copyAct)
        self.packToolBar.addAction(self.packTreeView.cutAct)
        self.packToolBar.addAction(self.packTreeView.pasteAct)
        self.packToolBar.addAction(self.packTreeView.delClearAct)
        self.packToolBar.addAction(self.packTreeView.addAct)

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
        self.mainTabWidget.currItemChanged.connect(self.onCurrTabItemChanged)
        self.packTreeView.selectionModel().currentChanged.connect(self.onSelectedPackItemChanged)
        self.packTreeView.doubleClicked.connect(self.onDoubleClicked)

        self.packTreeView.wheelClicked.connect(self.mainTabWidget.openItemInBgTab)
        self.packTreeView.openInBgTabClicked.connect(self.mainTabWidget.openItemInBgTab)
        self.packTreeView.openInNewTabClicked.connect(self.mainTabWidget.openItemInNewTab)
        self.packTreeView.openInCurrTabClicked.connect(self.mainTabWidget.openItem)
        self.packTreeView.openInNewWindowClicked.connect(self.mainTabWidget.openItemInNewWindow)

        self.packTreeModel.rowsRemoved.connect(self.mainTabWidget.removePackTab)

    def onCurrTabItemChanged(self, item: QModelIndex):
        if self.packTreeView.autoScrollFromSrcAct.isChecked():
            self.packTreeView.setCurrentIndex(item)

    def onSelectedPackItemChanged(self, item: QModelIndex):
        if self.packTreeView.autoScrollToSrcAct.isChecked():
            self.mainTabWidget.openItem(item)

    def onDoubleClicked(self, item: QModelIndex):
        if not self.packTreeView.autoScrollToSrcAct.isChecked():
            self.mainTabWidget.openItemInNewTab(item)

    def removeTabsOfClosedRows(self, parent: QModelIndex, first: int, last: int):
        for row in range(first, last):
            packItem = self.packTreeModel.index(row, 0, parent)
            self.mainTabWidget.removePackTab(packItem)

    def setFocus2rightTree(self):
        tab: 'Tab' = self.mainTabWidget.currentWidget()
        if not tab.attrsTreeView.currentIndex().isValid():
            firstItem = tab.attrsTreeView.model().index(0, 0, QModelIndex())
            tab.attrsTreeView.setCurrentIndex(firstItem)
        self.mainTabWidget.currentWidget().attrsTreeView.setFocus()

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

        size = settings.value('size', DEFAULT_MAINWINDOW_SIZE)
        self.resize(size)

        splitterLeftSize = settings.value('leftZoneSize', QSize(300, 624))
        splitterRightSize = settings.value('rightZoneSize', QSize(300, 624))
        self.leftLayoutWidget.resize(splitterLeftSize)
        self.rightLayoutWidget.resize(splitterRightSize)

        fontSizeFilesView = settings.value('fontSizeFilesView',
                                           PacksTable.defaultFont.pointSize())
        PacksTable.defaultFont.setPointSize(int(fontSizeFilesView))

        fontSizeDetailedView = settings.value('fontSizeDetailedView',
                                              DetailedInfoTable.defaultFont.pointSize())
        DetailedInfoTable.defaultFont.setPointSize(int(fontSizeDetailedView))

        openedAasFiles = settings.value('openedAasFiles', set())
        for file in openedAasFiles:
            try:
                self.packTreeView.openPack(file)
            except OSError:
                pass

    def writeSettings(self):
        settings = QSettings(ACPLT, APPLICATION_NAME)
        settings.setValue('theme', self.currTheme)
        settings.setValue('size', self.size())
        settings.setValue('leftZoneSize', self.leftLayoutWidget.size())
        settings.setValue('rightZoneSize', self.rightLayoutWidget.size())
        settings.setValue('openedAasFiles', self.packTreeModel.openedFiles())
        settings.setValue('fontSizeFilesView', PacksTable.defaultFont.pointSize())
        settings.setValue('fontSizeDetailedView', DetailedInfoTable.defaultFont.pointSize())

# ToDo logs insteads of prints
