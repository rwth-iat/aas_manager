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

from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from aas_editor.settings.app_settings import *
from aas_editor.settings.icons import APP_ICON, EXIT_ICON, SETTINGS_ICON
from aas_editor.settings_dialog import SettingsDialog
from aas_editor.widgets.compliance_tool import ComplianceToolDialog
from aas_editor.widgets import AddressLine
from aas_editor import design
from aas_editor.models import DetailedInfoTable, PacksTable
from aas_editor.utils.util import toggleStylesheet
from aas_editor import dialogs


class EditorApp(QMainWindow, design.Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.currTheme = DEFAULT_THEME

        dialogs.AASReferenceGroupBox.CHOOSE_FRM_VIEW = self.mainTreeView
        AddressLine.setModel(self.mainTreeView.model())
        welcomeTabKwargs = self.mainTabWidget.tabClsKwargs if self.mainTabWidget.tabClsKwargs else {}
        welcomeTab = self.mainTabWidget.addTab(self.mainTabWidget.tabCls(parent=self.mainTabWidget, **welcomeTabKwargs),
                                               "Welcome")
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
                               triggered=lambda: self.close())

        self.aboutDialogAct = QAction("About", self,
                                      statusTip=f"Show information about {APPLICATION_NAME}",
                                      triggered=lambda: dialogs.AboutDialog(self).exec())

        self.complToolDialogAct = QAction("Compliance tool", self,
                                      statusTip="Open compliance tool",
                                      triggered=lambda: ComplianceToolDialog(self).exec())

        self.importToolAct = QAction("Table import tool", self,
                                      statusTip="Switch to table import mode",
                                      triggered=lambda: self.showImportApp())

        self.settingsDialogAct = QAction(SETTINGS_ICON, "Settings", self,
                                         statusTip=f"Edit application settings",
                                         triggered=lambda: SettingsDialog(self).exec())

        # Theme actions
        self.themeActs = []
        for theme in THEMES:
            themeAct = QAction(theme, self,
                               statusTip=f"Choose {theme} theme",
                               triggered=lambda: self.toggleThemeSlot())
            self.themeActs.append(themeAct)

        self.setHOrientationAct = QAction("Horizontal", self,
                                          statusTip=f"Set horizontal orientation",
                                          triggered=lambda: self.setOrientation(QtCore.Qt.Horizontal))
        self.setVOrientationAct = QAction("Vertical", self,
                                          statusTip=f"Set vertical orientation",
                                          triggered=lambda: self.setOrientation(QtCore.Qt.Vertical))

    def showImportApp(self):
        self.writeSettings()
        from aas_editor.importApp import ImportApp
        ImportApp(parent=self).show()

    def initMenu(self):
        self.menubar = QMenuBar(self)
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        self.menuFile = QMenu("&File", self.menubar)
        self.menuFile.addAction(self.mainTreeView.newPackAct)
        self.menuFile.addAction(self.mainTreeView.openPackAct)

        self.menuFile.addSeparator()
        self.menuOpenRecent = QMenu("Open Recent", self.menuFile)
        for recentFileAct in self.mainTreeView.recentFileActs:
            self.menuOpenRecent.addAction(recentFileAct)
        self.menuFile.addAction(self.menuOpenRecent.menuAction())
        self.mainTreeView.recentFilesSeparator = self.menuFile.addSeparator()
        self.mainTreeView.updateRecentFileActs()

        self.menuFile.addAction(self.mainTreeView.saveAct)
        self.menuFile.addAction(self.mainTreeView.saveAsAct)
        self.menuFile.addAction(self.mainTreeView.saveAllAct)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.settingsDialogAct)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.mainTreeView.closeAct)
        self.menuFile.addAction(self.mainTreeView.closeAllAct)
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
        self.menuView.addAction(self.mainTreeView.zoomInAct)
        self.menuView.addAction(self.mainTreeView.zoomOutAct)
        self.menuView.addSection("Detailed view")
        self.menuView.addAction(self.mainTabWidget.zoomInAct)
        self.menuView.addAction(self.mainTabWidget.zoomOutAct)

        self.menuNavigate = QMenu("&Navigate", self.menubar)
        self.menuNavigate.addAction(self.mainTreeView.autoScrollToSrcAct)
        self.menuNavigate.addAction(self.mainTreeView.autoScrollFromSrcAct)
        self.menuNavigate.addSeparator()
        self.menuNavigate.addAction(self.mainTreeView.openInNewTabAct)
        self.menuNavigate.addAction(self.mainTreeView.openInCurrTabAct)
        self.menuNavigate.addAction(self.mainTreeView.openInBackgroundAct)
        self.menuNavigate.addAction(self.mainTreeView.openInNewWindowAct)

        self.menuTools = QMenu("&Tools", self.menubar)
        self.menuTools.addAction(self.complToolDialogAct)
        self.menuTools.addAction(self.importToolAct)

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
        menuSettings.addAction(self.mainTreeView.zoomInAct)
        menuSettings.addAction(self.mainTreeView.zoomOutAct)
        menuSettings.addAction(self.mainTreeView.autoScrollToSrcAct)
        menuSettings.addAction(self.mainTreeView.autoScrollFromSrcAct)
        settingsBtn.setMenu(menuSettings)

        self.toolBar.addWidget(settingsBtn)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.mainTreeView.saveAllAct)
        self.toolBar.addAction(self.mainTreeView.saveAct)
        self.toolBar.addAction(self.mainTreeView.openPackAct)
        self.toolBar.addAction(self.mainTreeView.newPackAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.mainTreeView.collapseAllAct)
        self.toolBar.addAction(self.mainTreeView.expandAllAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.mainTreeView.undoAct)
        self.toolBar.addAction(self.mainTreeView.redoAct)
        self.toolBar.addAction(self.mainTreeView.editCreateInDialogAct)
        self.toolBar.addAction(self.mainTreeView.addAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.mainTreeView.shellViewAct)

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
        self.mainTreeView.selectionModel().currentChanged.connect(self.onSelectedPackItemChanged)
        self.mainTreeView.doubleClicked.connect(self.onDoubleClicked)

        self.mainTreeView.wheelClicked.connect(self.mainTabWidget.openItemInBgTab)
        self.mainTreeView.openInBgTabClicked.connect(self.mainTabWidget.openItemInBgTab)
        self.mainTreeView.openInNewTabClicked.connect(self.mainTabWidget.openItemInNewTab)
        self.mainTreeView.openInCurrTabClicked.connect(self.mainTabWidget.openItem)
        self.mainTreeView.openInNewWindowClicked.connect(self.mainTabWidget.openItemInNewWindow)

        self.packTreeModel.rowsRemoved.connect(self.mainTabWidget.removePackTab)

    def onCurrTabItemChanged(self, item: QModelIndex):
        if self.mainTreeView.autoScrollFromSrcAct.isChecked():
            if not item.siblingAtColumn(0) == self.mainTreeView.currentIndex().siblingAtColumn(0):
                self.mainTreeView.setCurrentIndex(item)

    def onSelectedPackItemChanged(self, item: QModelIndex):
        if self.mainTreeView.autoScrollToSrcAct.isChecked():
            self.mainTabWidget.openItem(item)

    def onDoubleClicked(self, item: QModelIndex):
        if not self.mainTreeView.autoScrollToSrcAct.isChecked():
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
            a0.accept()
        elif self.isWindowModified():
            reply = QMessageBox.question(self, 'Window Close',
                                         'Do you want to save files before closing the window?',
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                         QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.mainTreeView.saveAll()
                a0.accept()
            elif reply == QMessageBox.No:
                a0.accept()
            else:
                return a0.ignore()
        self.writeSettings()

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
        self.mainLayoutWidget.resize(splitterLeftSize)
        self.subLayoutWidget.resize(splitterRightSize)

        # set previously used fontsizes in trees
        fontSizeFilesView = AppSettings.FONTSIZE_FILES_VIEW.value()
        fontSizeDetailedView = AppSettings.FONTSIZE_DETAILED_VIEW.value()
        PacksTable.currFont.setPointSize(fontSizeFilesView)
        DetailedInfoTable.currFont.setPointSize(fontSizeDetailedView)

        # try to open previously opened files
        openedAasFiles = AppSettings.OPENED_AAS_FILES.value()
        for file in openedAasFiles:
            try:
                self.mainTreeView.openPack(file)
            except OSError:
                pass
            self.packTreeModel.setData(QModelIndex(), [], UNDO_ROLE)

        # set previous tree states
        packTreeViewHeader = self.mainTreeView.header()
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
        AppSettings.LEFT_ZONE_SIZE.setValue(self.mainLayoutWidget.size())
        AppSettings.RIGHT_ZONE_SIZE.setValue(self.subLayoutWidget.size())
        AppSettings.OPENED_AAS_FILES.setValue(self.packTreeModel.openedFiles())
        AppSettings.FONTSIZE_FILES_VIEW.setValue(PacksTable.currFont.pointSize())
        AppSettings.FONTSIZE_DETAILED_VIEW.setValue(DetailedInfoTable.currFont.pointSize())
        AppSettings.PACKTREEVIEW_HEADER_STATE.setValue(self.mainTreeView.header().saveState())
        AppSettings.TABTREEVIEW_HEADER_STATE.setValue(self.mainTabWidget.currentWidget().attrsTreeView.header().saveState())
        # AppSettings.DEFAULT_NEW_FILETYPE_FILTER.setValue(self.packTreeView.defaultNewFileTypeFilter)

# ToDo logs insteads of prints
