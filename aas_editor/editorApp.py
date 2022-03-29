#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
import json

from PyQt5 import QtCore
from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from aas_editor.settings import EXTENDED_COLUMNS_IN_PACK_TABLE
from aas_editor.settings.app_settings import *
from aas_editor.settings.icons import APP_ICON, EXIT_ICON, SETTINGS_ICON
from aas_editor.settings_dialog import SettingsDialog
from aas_editor.dialogs import AboutDialog
from aas_editor.widgets.compliance_tool import ComplianceToolDialog
from aas_editor.widgets import SearchBar, AddressLine
from aas_editor import design
from aas_editor.models import DetailedInfoTable, PacksTable
from aas_editor.models.table_import import ImportTable
from aas_editor.utils.util import toggleStylesheet
from aas_editor.widgets.tab import Tab
from aas_editor import dialogs


class EditorApp(QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.currTheme = DEFAULT_THEME

        columns_in_packs_table = list(DEFAULT_COLUMNS_IN_PACKS_TABLE)
        columns_in_packs_table.extend(EXTENDED_COLUMNS_IN_PACK_TABLE)
        self.packTreeModel = ImportTable(columns_in_packs_table)
        self.packTreeView.setModelWithProxy(self.packTreeModel)
        for column in range(len(columns_in_packs_table), 2, -1):
            self.packTreeView.hideColumn(column)
        dialogs.AASReferenceGroupBox.CHOOSE_FRM_VIEW = self.packTreeView

        AddressLine.setModel(self.packTreeView.model())

        welcomeTab = self.mainTabWidget.addTab(Tab(parent=self.mainTabWidget), "Welcome")
        self.mainTabWidget.widget(welcomeTab).searchBar.showFocused()

        self.initActions()
        self.initMenu()
        self.initToolbars()
        self.buildHandlers()
        self.readSettings()
        self.setWindowIcon(APP_ICON)

    # noinspection PyArgumentList
    def initActions(self):
        self.exitAct = QAction(EXIT_ICON, "E&xit", self,
                               statusTip="Exit the application",
                               triggered=self.close)

        self.aboutDialogAct = QAction("About", self,
                                      statusTip=f"Show information about {APPLICATION_NAME}",
                                      triggered=AboutDialog(self).exec)

        self.complToolDialogAct = QAction("Compliance tool", self,
                                      statusTip="Open compliance tool",
                                      triggered=lambda: ComplianceToolDialog(self).exec())

        self.settingsDialogAct = QAction(SETTINGS_ICON, "Settings", self,
                                         statusTip=f"Edit application settings",
                                         triggered=lambda: SettingsDialog(self).exec())

        # Theme actions
        self.themeActs = []
        for theme in THEMES:
            themeAct = QAction(theme, self,
                               statusTip=f"Choose {theme} theme",
                               triggered=self.toggleThemeSlot)
            self.themeActs.append(themeAct)

        self.setHOrientationAct = QAction("Horizontal", self,
                                          statusTip=f"Set horizontal orientation",
                                          triggered=lambda: self.setOrientation(QtCore.Qt.Horizontal))
        self.setVOrientationAct = QAction("Vertical", self,
                                          statusTip=f"Set vertical orientation",
                                          triggered=lambda: self.setOrientation(QtCore.Qt.Vertical))

    def initMenu(self):
        self.menubar = QMenuBar(self)
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        self.menuFile = QMenu("&File", self.menubar)
        self.menuFile.addAction(self.packTreeView.newPackAct)
        self.menuFile.addAction(self.packTreeView.openPackAct)

        self.menuFile.addSeparator()
        self.menuOpenRecent = QMenu("Open Recent", self.menuFile)
        for recentFileAct in self.packTreeView.recentFileActs:
            self.menuOpenRecent.addAction(recentFileAct)
        self.menuFile.addAction(self.menuOpenRecent.menuAction())
        self.packTreeView.recentFilesSeparator = self.menuFile.addSeparator()
        self.packTreeView.updateRecentFileActs()

        self.menuFile.addAction(self.packTreeView.saveAct)
        self.menuFile.addAction(self.packTreeView.saveAsAct)
        self.menuFile.addAction(self.packTreeView.saveAllAct)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.settingsDialogAct)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.packTreeView.closeAct)
        self.menuFile.addAction(self.packTreeView.closeAllAct)
        self.menuFile.addAction(self.exitAct)

        self.menuView = QMenu("&View", self.menubar)
        self.menuChooseTheme = QMenu("Choose Theme", self.menuView)
        for themeAct in self.themeActs:
            self.menuChooseTheme.addAction(themeAct)
        self.menuView.addAction(self.menuChooseTheme.menuAction())
        self.menuAppearance = QMenu("Appearance", self.menuView)
        self.menuAppearance.addAction(self.toolBar.toggleViewAction())
        self.menuAppearance.addAction(self.searchBarPack.toggleViewAction())
        self.menuView.addAction(self.menuAppearance.menuAction())
        self.menuAppearance = QMenu("Orientation", self.menuView)
        self.menuAppearance.addAction(self.setHOrientationAct)
        self.menuAppearance.addAction(self.setVOrientationAct)
        self.menuView.addAction(self.menuAppearance.menuAction())
        self.menuView.addSection("AAS file view")
        self.menuView.addAction(self.packTreeView.zoomInAct)
        self.menuView.addAction(self.packTreeView.zoomOutAct)
        self.menuView.addSection("Detailed view")
        self.menuView.addAction(self.mainTabWidget.zoomInAct)
        self.menuView.addAction(self.mainTabWidget.zoomOutAct)

        self.menuNavigate = QMenu("&Navigate", self.menubar)
        self.menuNavigate.addAction(self.packTreeView.autoScrollToSrcAct)
        self.menuNavigate.addAction(self.packTreeView.autoScrollFromSrcAct)
        self.menuNavigate.addSeparator()
        self.menuNavigate.addAction(self.packTreeView.openInNewTabAct)
        self.menuNavigate.addAction(self.packTreeView.openInCurrTabAct)
        self.menuNavigate.addAction(self.packTreeView.openInBackgroundAct)
        self.menuNavigate.addAction(self.packTreeView.openInNewWindowAct)

        self.menuTools = QMenu("&Tools", self.menubar)
        self.menuTools.addAction(self.complToolDialogAct)

        self.menuHelp = QMenu("&Help", self.menubar)
        self.menuHelp.addAction(self.aboutDialogAct)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuNavigate.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

    def initToolbars(self):
        settingsBtn = QToolButton(icon=SETTINGS_ICON)
        settingsBtn.setPopupMode(QToolButton.InstantPopup)
        menuSettings = QMenu("Settings")
        menuSettings.addAction(self.packTreeView.zoomInAct)
        menuSettings.addAction(self.packTreeView.zoomOutAct)
        menuSettings.addAction(self.packTreeView.autoScrollToSrcAct)
        menuSettings.addAction(self.packTreeView.autoScrollFromSrcAct)
        settingsBtn.setMenu(menuSettings)

        self.toolBar.addWidget(settingsBtn)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.packTreeView.saveAllAct)
        self.toolBar.addAction(self.packTreeView.saveAct)
        self.toolBar.addAction(self.packTreeView.openPackAct)
        self.toolBar.addAction(self.packTreeView.newPackAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.packTreeView.collapseAllAct)
        self.toolBar.addAction(self.packTreeView.expandAllAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.packTreeView.addAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.packTreeView.shellViewAct)

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
            if not item.siblingAtColumn(0) == self.packTreeView.currentIndex().siblingAtColumn(0):
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
        # set previously used theme
        theme = AppSettings.THEME.value()
        self.toggleTheme(theme)

        # set previously used mainwindow size and orientation
        size = AppSettings.SIZE.value()
        self.resize(size)
        orientation = AppSettings.ORIENTATION.value()
        self.setOrientation(orientation)

        # set previously used sizes of right ans left layouts
        splitterLeftSize = AppSettings.LEFT_ZONE_SIZE.value()
        splitterRightSize = AppSettings.RIGHT_ZONE_SIZE.value()
        self.leftLayoutWidget.resize(splitterLeftSize)
        self.rightLayoutWidget.resize(splitterRightSize)

        # set previously used fontsizes in trees
        fontSizeFilesView = AppSettings.FONTSIZE_FILES_VIEW.value()
        fontSizeDetailedView = AppSettings.FONTSIZE_DETAILED_VIEW.value()
        PacksTable.currFont.setPointSize(fontSizeFilesView)
        DetailedInfoTable.currFont.setPointSize(fontSizeDetailedView)

        # try to open previously opened files
        openedAasFiles = AppSettings.OPENED_AAS_FILES.value()
        for file in openedAasFiles:
            try:
                self.packTreeView.openPack(file)
            except OSError:
                pass
            self.packTreeModel.setData(QModelIndex(), [], UNDO_ROLE)

        # set previous tree states
        packTreeViewHeader = self.packTreeView.header()
        packTreeViewHeaderState = AppSettings.PACKTREEVIEW_HEADER_STATE.value()
        if packTreeViewHeaderState:
            packTreeViewHeader.restoreState(packTreeViewHeaderState)
        with open(AppSettings.PACKTREEVIEW_HEADER_CUSTOM_COLUMN_LISTS_FILE) as json_file:
            customLists = json.load(json_file)
            packTreeViewHeader.setCustomLists(customLists)
        packTreeViewHeader.initMenu()

        tabTreeViewHeaderState = AppSettings.TABTREEVIEW_HEADER_STATE.value()
        if tabTreeViewHeaderState:
            self.mainTabWidget.currentWidget().attrsTreeView.header().restoreState(tabTreeViewHeaderState)

    def writeSettings(self):
        AppSettings.THEME.setValue(self.currTheme)
        AppSettings.SIZE.setValue(self.size())
        AppSettings.LEFT_ZONE_SIZE.setValue(self.leftLayoutWidget.size())
        AppSettings.RIGHT_ZONE_SIZE.setValue(self.rightLayoutWidget.size())
        AppSettings.OPENED_AAS_FILES.setValue(self.packTreeModel.openedFiles())
        AppSettings.FONTSIZE_FILES_VIEW.setValue(PacksTable.currFont.pointSize())
        AppSettings.FONTSIZE_DETAILED_VIEW.setValue(DetailedInfoTable.currFont.pointSize())
        AppSettings.PACKTREEVIEW_HEADER_STATE.setValue(self.packTreeView.header().saveState())
        AppSettings.TABTREEVIEW_HEADER_STATE.setValue(self.mainTabWidget.currentWidget().attrsTreeView.header().saveState())
        # AppSettings.DEFAULT_NEW_FILETYPE_FILTER.setValue(self.packTreeView.defaultNewFileTypeFilter)

# ToDo logs insteads of prints
