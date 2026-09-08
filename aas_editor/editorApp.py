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
import logging
import webbrowser
from pathlib import Path

from PyQt6.QtCore import QModelIndex, QTimer, pyqtSignal
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

import aas_editor.widgets as widgets
import aas_editor.widgets.messsageBoxes
import aas_editor.widgets.groupBoxes
from aas_editor.settings.app_settings import *
from aas_editor.utils.recovery import find_recovery_files, delete_recovery_file, cleanup_recovery_dir
from aas_editor.package import Package
from aas_editor.utils.exceptionhook import set_crash_callback
from aas_editor.settings.icons import EXIT_ICON, SETTINGS_ICON, NEW_PACK_ICON
from aas_editor.settings import APPLICATION_NAME, REPORT_ERROR_LINK
from aas_editor.widgets.settingWidgets import SettingsDialog
from aas_editor.tools.aas_test.aas_test_engines_tool import AasTestEnginesToolDialog
from aas_editor.widgets import AddressLine
from aas_editor import design
from aas_editor.models import DetailedInfoTable, PacksTable
from aas_editor.utils.util import toggleStylesheet
from aas_editor.treeviews.base import HeaderView


class EditorApp(QMainWindow, design.Ui_MainWindow):
    closed = pyqtSignal()

    def __init__(self, fileToOpen=None, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.loadThemes()

        widgets.groupBoxes.ModelReferenceGroupBox.CHOOSE_FRM_VIEW = self.mainTreeView
        AddressLine.setModel(self.mainTreeView.model())
        welcomeTabKwargs = self.mainTabWidget.tabClsKwargs if self.mainTabWidget.tabClsKwargs else {}
        welcomeTab = self.mainTabWidget.addTab(self.mainTabWidget.tabCls(parent=self.mainTabWidget, **welcomeTabKwargs),
                                               "Welcome")

        self.initActions()
        self.initMenu()
        self.initToolbars()
        self.buildHandlers()
        self.restoreSettingsFromLastSession()
        set_crash_callback(self._save_recovery_files)

        # sys.excepthook misses native crashes (segfaults, OOM kills), which run no
        # Python and never reach _save_recovery_files. Persist periodically instead.
        self._recoveryTimer = QTimer(self)
        self._recoveryTimer.setInterval(RECOVERY_INTERVAL_MS)
        self._recoveryTimer.timeout.connect(self._save_recovery_files)
        self._recoveryTimer.start()
        # Shown once on failure and cleared once writing recovers.
        self._recoveryWriteFailed = False
        # Synced to settings only when it changes (open/close), not on every tick.
        self._lastPersistedOpenFiles = None
        # Permanent widget, not showMessage(): transient status tips (menu hover)
        # do not overwrite it, so the warning stays until writing recovers.
        self._recoveryStatusLabel = QLabel()
        self._recoveryStatusLabel.setStyleSheet("color: #c0392b;")
        self._recoveryStatusLabel.hide()
        self.statusBar().addPermanentWidget(self._recoveryStatusLabel)
        if fileToOpen:
            self.openAASFile(fileToOpen)
        else:
            self.openLastSessionFiles()

    def loadThemes(self):
        self.themes = {}
        for file in THEMES_FOLDER.iterdir():
            if file.suffix == ".qss":
                self.themes[file.stem] = str(file)
        self.currTheme = DEFAULT_THEME

    # noinspection PyArgumentList
    def initActions(self):
        self.exitAct = QAction(EXIT_ICON, "E&xit", self,
                               statusTip="Exit the application",
                               triggered=lambda: self.close())

        self.aboutDialogAct = QAction("About", self,
                                      statusTip=f"Show information about {APPLICATION_NAME}",
                                      triggered=lambda: widgets.messsageBoxes.AboutMessageBox(self).exec())

        self.testEnginesToolDialogAct = QAction("AAS Test tool", self,
                                          statusTip="Open AAS Test Engines tool",
                                          triggered=lambda: AasTestEnginesToolDialog(self).exec())

        self.handoverDocumentationToolDialogAct = QAction("Handover Documentation tool", self,
                                          statusTip="Open Handover Documentation tool",
                                          triggered=self.openHandoverDocumentationTool)

        self.importToolAct = QAction("Excel AAS Generator tool", self,
                                     statusTip="Open Excel AAS Generator tool",
                                     triggered=lambda: self.showImportApp())

        self.settingsDialogAct = QAction(SETTINGS_ICON, "Settings", self,
                                         statusTip=f"Edit application settings",
                                         triggered=lambda: SettingsDialog(self).exec())

        self.reportBugAct = QAction("Report Bug", self,
                                    statusTip="Report an error found",
                                    triggered=lambda: webbrowser.open(REPORT_ERROR_LINK))

        # Theme actions
        self.themeActs = []
        for theme in self.themes:
            self.themeActs.append(QAction(theme, self,
                                          statusTip=f"Choose {theme} theme",
                                          triggered=lambda: self.toggleThemeSlot()))

        self.setHOrientationAct = QAction("Horizontal", self,
                                          statusTip=f"Set horizontal orientation",
                                          triggered=lambda: self.setOrientation(QtCore.Qt.Orientation.Horizontal))
        self.setVOrientationAct = QAction("Vertical", self,
                                          statusTip=f"Set vertical orientation",
                                          triggered=lambda: self.setOrientation(QtCore.Qt.Orientation.Vertical))

    def showImportApp(self):
        self.writeSettings()
        from aas_editor.tools.import_feature.import_app import ImportApp
        self.hide()
        importApp = ImportApp()
        importApp.closed.connect(self.show)
        importApp.show()

    def initMenu(self):
        self.menubar = QMenuBar(self)
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        self.menuFile = QMenu("&File", self.menubar)
        self.menuNewAasFile = QMenu("New AAS file...", self.menuFile)
        self.menuNewAasFile.setIcon(NEW_PACK_ICON)
        for newPackAct in self.mainTreeView.newPackActs:
            self.menuNewAasFile.addAction(newPackAct)
        self.menuFile.addMenu(self.menuNewAasFile)
        self.menuFile.addAction(self.mainTreeView.openPackAct)
        # self.menuFile.addAction(self.mainTreeView.openPackFromServerAct)

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

        self.menuTools = QMenu("&Tools", self.menubar)
        self.menuTools.addAction(self.testEnginesToolDialogAct)
        self.menuTools.addAction(self.handoverDocumentationToolDialogAct)
        self.menuTools.addAction(self.importToolAct)

        self.menuHelp = QMenu("&Help", self.menubar)
        self.menuHelp.addAction(self.aboutDialogAct)
        self.menuHelp.addAction(self.reportBugAct)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addMenu(self.mainTreeView.header().menu)
        self.menubar.addAction(self.menuNavigate.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

    def initToolbars(self):
        settingsBtn = QToolButton(icon=SETTINGS_ICON)
        settingsBtn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
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
        # self.toolBar.addAction(self.mainTreeView.openPackFromServerAct)
        self.toolBar.addAction(self.mainTreeView.newPackActs[0])
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.mainTreeView.collapseAllAct)
        self.toolBar.addAction(self.mainTreeView.expandAllAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.mainTreeView.undoAct)
        self.toolBar.addAction(self.mainTreeView.redoAct)
        self.toolBar.addAction(self.mainTreeView.editCreateInDialogAct)
        self.toolBar.addAction(self.mainTreeView.addAct)

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
        if theme in self.themes:
            toggleStylesheet(self.themes[theme])
            self.currTheme = theme

    def closeEvent(self, a0: QCloseEvent) -> None:
        # Edits made in a detached tab window set the flag on that window, not on this one,
        # so rebuild it from the packages before deciding whether to ask for saving
        self.mainTreeView.updateWindowModified()
        if not self.packTreeModel.openedFiles():
            a0.accept()
        elif self.isWindowModified():
            reply = QMessageBox.question(self, 'Window Close',
                                         'Do you want to save files before closing the window?',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                self.mainTreeView.saveAll()
                a0.accept()
            elif reply == QMessageBox.StandardButton.No:
                # Discarding: stop recovery writes and drop the recovery files so the
                # next launch does not offer to restore discarded changes.
                self._recoveryTimer.stop()
                for pkg in self.packTreeModel.openedPacks():
                    if pkg.changed:
                        pkg.delete_recovery(RECOVERY_DIR)
                a0.accept()
            else:
                return a0.ignore()
        self.writeSettings()
        self.closed.emit()

    def restoreSettingsFromLastSession(self):
        self.applyLastSessionTheme()
        self.applyLastSessionMainWindowSize()
        self.applyLastSessionOrientation()
        self.applyLastSessionLayouts()
        self.applyLastSessionTreeFontSizes()
        self.applyLastSessionTreeStates()

    def openLastSessionFiles(self):
        recovery_map = find_recovery_files(RECOVERY_DIR)
        openedAasFiles = AppSettings.AAS_FILES_TO_OPEN_ON_START.value()
        # Recovery files restored this launch: kept through the sweep below until their
        # first save, so a native crash before that save still has the restored data.
        keptRecoveries = []
        for file in openedAasFiles:
            # resolve() to match find_recovery_files()'s resolved keys, so a
            # symlinked or '..'-containing path still lines up with its recovery.
            file_path = Path(file).resolve()
            if file_path in recovery_map:
                reply = QMessageBox.question(
                    self, "Restore unsaved changes",
                    f"A recovery file was found for:\n{file_path.name}\n\n"
                    "The app may have crashed with unsaved changes.\n"
                    "Do you want to restore the last auto-saved version?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes,
                )
                if reply == QMessageBox.StandardButton.Yes:
                    rec = recovery_map[file_path]
                    # Kept whether or not the restore succeeds: a failed restore still
                    # keeps the recovery data as it may be salvageable by hand.
                    keptRecoveries.append(rec)
                    try:
                        pack = Package.restore_from_recovery(rec, file_path)
                    except Exception:
                        logging.exception("Failed to restore recovery file %s", rec)
                        QMessageBox.warning(
                            self, "Restore failed",
                            f"The recovery file for {file_path.name} could not be opened.\n\n"
                            f"It was kept at:\n{rec}\n\n"
                            "Opening the last saved version instead.")
                        self.openAASFile(file)
                    else:
                        self.mainTreeView.add_pack_to_tree(pack)
                        self.packTreeModel.setData(QModelIndex(), [], UNDO_ROLE)
                        # Restored content is unsaved until the user writes it back
                        pack.changed = True
                        self.setWindowModified(True)
                else:
                    delete_recovery_file(recovery_map[file_path])
                    self.openAASFile(file)
            else:
                self.openAASFile(file)

        # Drop everything left in the recovery dir except the entries just restored:
        # declined files, orphans (recovery for files no longer opened on start),
        # stale .meta.json and leftover .tmp writes. Keeps the dir from growing forever.
        cleanup_recovery_dir(RECOVERY_DIR, keptRecoveries)

    def _save_recovery_files(self):
        # Persist open-file list before crash exits — closeEvent won't run. Restore
        # matches recovery files against this list, so it must stay current for a native
        # crash to offer them. Sync only when it changed to keep it off the disk on
        # every tick.
        openFiles = self.packTreeModel.openedFiles()
        if openFiles != self._lastPersistedOpenFiles:
            AppSettings.AAS_FILES_TO_OPEN_ON_START.setValue(openFiles)
            SETTINGS.sync()
            self._lastPersistedOpenFiles = openFiles
        writeFailed = False
        for pkg in self.packTreeModel.openedPacks():
            # Per-package flag: the window modified flag is shared and gets reset
            # whenever any package is saved or closed
            if pkg.changed and pkg.file and pkg.file.exists():
                try:
                    pkg.write_recovery(RECOVERY_DIR)
                except Exception:
                    # Never let a failed recovery write abort the crash handler or the
                    # timer, but log it: a silent failure means the user believes they
                    # are protected while no recovery is being written (disk full, etc.).
                    writeFailed = True
                    logging.exception("Failed to write recovery file for %s", pkg.file)
        self._reportRecoveryWriteStatus(writeFailed)

    def _reportRecoveryWriteStatus(self, writeFailed: bool):
        """Show a non-blocking status-bar warning while recovery writes are failing.

        Informant only: no dialog, no interruption. Shown once on the transition to
        failure and cleared once writes recover, so a persistently failing write does
        not spam a message on every tick.
        """
        if writeFailed and not self._recoveryWriteFailed:
            self._recoveryStatusLabel.setText(
                "⚠ Auto-recovery could not be saved — unsaved changes are not backed up. "
                "See log for details.")
            self._recoveryStatusLabel.show()
        elif not writeFailed and self._recoveryWriteFailed:
            self._recoveryStatusLabel.hide()
        self._recoveryWriteFailed = writeFailed

    def openAASFile(self, filePath: str):
        """Return the opened Package, or None if it could not be opened."""
        pack = None
        try:
            pack = self.mainTreeView.openPack(filePath)
        except OSError:
            pass
        self.packTreeModel.setData(QModelIndex(), [], UNDO_ROLE)
        return pack  # None if the file could not be opened

    def applyLastSessionTreeStates(self):
        packTreeViewHeader: HeaderView = self.mainTreeView.header()
        packTreeViewHeaderState = AppSettings.PACKTREEVIEW_HEADER_STATE.value()
        if packTreeViewHeaderState:
            packTreeViewHeader.restoreState(packTreeViewHeaderState)
        else:
            packTreeViewHeader.showSectionWithNames(DEFAULT_COLUMNS_IN_PACKS_TABLE_TO_SHOW, only=True)
        with open(AppSettings.PACKTREEVIEW_HEADER_CUSTOM_COLUMN_LISTS_FILE) as json_file:
            customLists = json.load(json_file)
            packTreeViewHeader.setCustomLists(customLists)
        packTreeViewHeader.initMenu()
        tabTreeViewHeaderState = AppSettings.TABTREEVIEW_HEADER_STATE.value()
        if tabTreeViewHeaderState:
            self.mainTabWidget.currentWidget().attrsTreeView.header().restoreState(tabTreeViewHeaderState)

    def applyLastSessionTreeFontSizes(self):
        fontSizeFilesView = AppSettings.FONTSIZE_FILES_VIEW.value()
        fontSizeDetailedView = AppSettings.FONTSIZE_DETAILED_VIEW.value()
        PacksTable.currFont.setPointSize(fontSizeFilesView)
        DetailedInfoTable.currFont.setPointSize(fontSizeDetailedView)

    def applyLastSessionLayouts(self):
        splitterLeftSize = AppSettings.LEFT_ZONE_SIZE.value()
        splitterRightSize = AppSettings.RIGHT_ZONE_SIZE.value()
        self.mainLayoutWidget.resize(splitterLeftSize)
        self.subLayoutWidget.resize(splitterRightSize)

    def applyLastSessionOrientation(self):
        orientation = AppSettings.ORIENTATION.value()
        self.setOrientation(orientation)

    def applyLastSessionMainWindowSize(self):
        size = AppSettings.SIZE.value()
        self.resize(size)

    def applyLastSessionTheme(self):
        theme = AppSettings.THEME.value()
        self.toggleTheme(theme)

    def writeSettings(self):
        AppSettings.THEME.setValue(self.currTheme)
        AppSettings.SIZE.setValue(self.size())
        AppSettings.LEFT_ZONE_SIZE.setValue(self.mainLayoutWidget.size())
        AppSettings.RIGHT_ZONE_SIZE.setValue(self.subLayoutWidget.size())
        AppSettings.AAS_FILES_TO_OPEN_ON_START.setValue(self.packTreeModel.openedFiles())
        AppSettings.FONTSIZE_FILES_VIEW.setValue(PacksTable.currFont.pointSize())
        AppSettings.FONTSIZE_DETAILED_VIEW.setValue(DetailedInfoTable.currFont.pointSize())
        AppSettings.PACKTREEVIEW_HEADER_STATE.setValue(self.mainTreeView.header().saveState())
        AppSettings.TABTREEVIEW_HEADER_STATE.setValue(
            self.mainTabWidget.currentWidget().attrsTreeView.header().saveState())
        # AppSettings.DEFAULT_NEW_FILETYPE_FILTER.setValue(self.packTreeView.defaultNewFileType)

    def openHandoverDocumentationTool(self):
        from aas_editor.tools.handover_doc_llm.handover_documentation_tool import HandoverDocumentationToolDialog
        dialog = HandoverDocumentationToolDialog(self)
        dialog.handoverExtracted.connect(self.mainTreeView.add_handover_to_file)
        dialog.exec()

