from pathlib import Path

from PyQt5.QtCore import Qt, QModelIndex, QSettings
from PyQt5.QtGui import QDropEvent, QDragEnterEvent
from PyQt5.QtWidgets import QAction, QMessageBox, QFileDialog
from aas.model import AssetAdministrationShell

from aas_editor.package import Package, StoredFile
from aas_editor.settings import FILTER_AAS_FILES, CLASSES_INFO, PACKVIEW_ATTRS_INFO,\
    FILE_TYPE_FILTERS
from aas_editor.settings.app_settings import NAME_ROLE, OBJECT_ROLE, SC_SAVE_ALL, SC_OPEN, \
    PACKAGE_ROLE, MAX_RECENT_FILES, ACPLT, APPLICATION_NAME, OPEN_ICON, SAVE_ICON, SAVE_ALL_ICON, \
    OPENED_PACKS_ROLE, OPENED_FILES_ROLE, ADD_ITEM_ROLE, OPEN_DRAG_ICON, NEW_PACK_ICON, TYPE_ROLE, \
    VIEW_ICON, NOT_GIVEN, CLEAR_ROW_ROLE, FILE_DIALOG_OPTIONS
from aas_editor.utils.util_classes import ClassesInfo
from aas_editor.widgets import TreeView


class PackTreeView(TreeView):
    EMPTY_VIEW_MSG = "Drop AAS files here"
    EMPTY_VIEW_ICON = OPEN_DRAG_ICON

    def __init__(self, parent=None):
        super(PackTreeView, self).__init__(parent,
                                           emptyViewMsg=self.EMPTY_VIEW_MSG,
                                           emptyViewIcon=self.EMPTY_VIEW_ICON)
        PackTreeView.__instance = self
        self.recentFilesSeparator = None
        self.setAcceptDrops(True)
        self.setExpandsOnDoubleClick(False)

    # noinspection PyArgumentList
    def initActions(self):
        super(PackTreeView, self).initActions()
        self.addAct.setText("Add package")
        self.addAct.setEnabled(True)

        self.newPackAct = QAction(NEW_PACK_ICON, "&New AAS file", self,
                                  statusTip="Create new AAS file",
                                  triggered=self.newPackWithDialog,
                                  enabled=True)

        self.defNewFileTypeFilter = ""
        self.defNewFileTypeActs = []
        for typ in FILE_TYPE_FILTERS.keys():
            act = QAction(typ, self, checkable=True,
                          statusTip=f"Choose {typ} as standard initialisation file type",
                          triggered=self.toggleDefNewFileType)
            self.defNewFileTypeActs.append(act)

        self.openPackAct = QAction(OPEN_ICON, "&Open AAS file", self,
                                   shortcut=SC_OPEN,
                                   statusTip="Open AAS file",
                                   triggered=self.openPackWithDialog,
                                   enabled=True)

        # Recent files actions
        self.recentFileActs = []
        for i in range(MAX_RECENT_FILES):
            recentFileAct = QAction("", self,
                                    statusTip=f"Open recent file",
                                    triggered=self.openRecentSlot,
                                    visible=False)
            self.recentFileActs.append(recentFileAct)

        self.saveAct = QAction(SAVE_ICON, "Save", self,
                               statusTip="Save current file",
                               triggered=lambda: self.savePack(),
                               enabled=False)

        self.saveAsAct = QAction("Save As...", self,
                                 statusTip="Save current file as..",
                                 triggered=lambda: self.savePackAsWithDialog(),
                                 enabled=False)

        self.saveAllAct = QAction(SAVE_ALL_ICON, "&Save All", self,
                                  shortcut=SC_SAVE_ALL,
                                  statusTip="Save all files",
                                  triggered=self.saveAll,
                                  enabled=True)

        self.closeAct = QAction("Close AAS file", self,
                                statusTip="Close current file",
                                triggered=self.closeFileWithDialog,
                                enabled=False)

        self.closeAllAct = QAction("Close all", self,
                                   statusTip="Close all files",
                                   triggered=self.closeAllFilesWithDialog,
                                   enabled=False)

        self.autoScrollToSrcAct = QAction("Autoscroll to source", self,
                                          # icon=AUTOSCROLL_TO_SRC_ICON,
                                          toolTip="Autoscroll to source",
                                          statusTip="Autoscroll to source",
                                          checkable=True)
        self.autoScrollToSrcAct.toggle()
        self.autoScrollFromSrcAct = QAction("Autoscroll from source", self,
                                            # icon=AUTOSCROLL_FROM_SRC_ICON,
                                            toolTip="Autoscroll from source",
                                            statusTip="Autoscroll from source",
                                            checkable=True)
        self.autoScrollFromSrcAct.toggle()

        self.shellViewAct = QAction(VIEW_ICON, "Shell view", self,
                                    toolTip="Shell view",
                                    statusTip="Change to shell view",
                                    triggered=self.onShellViewPushed,
                                    checkable=True)

    def toggleDefNewFileType(self):
        #FIXME refactor
        action = self.sender()
        if action:
            typ = action.text()
            self.defNewFileTypeFilter = FILE_TYPE_FILTERS[typ]

    def onShellViewPushed(self):
        checked = self.shellViewAct.isChecked()

        packs = self.sourceModel().match(QModelIndex(), TYPE_ROLE, Package)
        if checked:
            for pack in packs:
                CLASSES_INFO[AssetAdministrationShell][PACKVIEW_ATTRS_INFO] = {"asset": {}, "submodel": {}}
                self.sourceModel().update(pack)

            rowsToHide = []
            for attr in ("submodels", "assets", "concept_descriptions", "others"):
                rowsToHide.extend(self.model().match(QModelIndex(), Qt.DisplayRole, attr))
            for row in rowsToHide:
                self.setRowHidden(row.row(), row.parent(), True)
        else:
            CLASSES_INFO[AssetAdministrationShell][PACKVIEW_ATTRS_INFO] = {}
            for pack in packs:
                self.sourceModel().update(pack)

    # noinspection PyUnresolvedReferences
    def initMenu(self):
        super(PackTreeView, self).initMenu()
        self.attrsMenu.addSeparator()
        self.attrsMenu.addAction(self.openPackAct)
        self.attrsMenu.addAction(self.saveAct)
        self.attrsMenu.addAction(self.saveAsAct)
        self.attrsMenu.addAction(self.saveAllAct)
        self.attrsMenu.addAction(self.closeAct)
        self.attrsMenu.addAction(self.closeAllAct)

        self.openInCurrTabAct.triggered.connect(
            lambda: self.openInCurrTabClicked.emit(self.currentIndex()))
        self.openInNewTabAct.triggered.connect(
            lambda: self.openInNewTabClicked.emit(self.currentIndex()))
        self.openInBackgroundAct.triggered.connect(
            lambda: self.openInBgTabClicked.emit(self.currentIndex()))
        self.openInNewWindowAct.triggered.connect(
            lambda: self.openInNewWindowClicked.emit(self.currentIndex()))

    def updateActions(self, index: QModelIndex):
        super(PackTreeView, self).updateActions(index)

        if index.isValid():
            self.openInCurrTabAct.setEnabled(True)
            self.openInNewTabAct.setEnabled(True)
            self.openInBackgroundAct.setEnabled(True)
            self.openInNewWindowAct.setEnabled(True)

        # update save and close actions
        self.saveAct.setEnabled(self.isSaveOk())
        self.saveAct.setText(f"Save {index.data(PACKAGE_ROLE)}")
        self.saveAct.setToolTip(f"Save {index.data(PACKAGE_ROLE)}")
        self.saveAsAct.setEnabled(self.isSaveOk())
        self.saveAllAct.setEnabled(self.isSaveAllOk())
        self.closeAct.setEnabled(self.isCloseOk())
        self.closeAllAct.setEnabled(self.isCloseAllOk())

        # update add action
        if not index.isValid():
            self.addAct.setEnabled(True)
            self.addAct.setText("Add package")

    def onDelClear(self):
        index = self.currentIndex()
        if isinstance(index.data(OBJECT_ROLE), Package):
            self.closeAct.trigger()
        else:
            super(PackTreeView, self).onDelClear()

    def isPasteOk(self, index: QModelIndex) -> bool:
        if not self.treeObjClipboard or not index.isValid():
            return False

        if super(PackTreeView, self).isPasteOk(index):
            return True

        obj2paste = self.treeObjClipboard[0]
        currObj = index.data(OBJECT_ROLE)

        if ClassesInfo.addType(type(currObj)) and isinstance(obj2paste, ClassesInfo.addType(type(currObj))):
            return True
        return False

    def isSaveOk(self) -> bool:
        pack = self.currentIndex().data(PACKAGE_ROLE)
        return True if pack else False

    def isCloseOk(self) -> bool:
        pack = self.currentIndex().data(PACKAGE_ROLE)
        return True if pack else False

    def isSaveAllOk(self) -> bool:
        return True if self.model().data(QModelIndex(), OPENED_PACKS_ROLE) else False

    def isCloseAllOk(self) -> bool:
        return True if self.model().data(QModelIndex(), OPENED_PACKS_ROLE) else False

    def onAddAct(self, objVal=None, parent: QModelIndex = None):
        parent = parent if parent else self.currentIndex()
        name = parent.data(NAME_ROLE)
        parentObj = parent.data(OBJECT_ROLE)

        if objVal:
            kwargs = {"parent": parent,
                      "rmDefParams": False,
                      "objVal": objVal}
        else:
            kwargs = {"parent": parent,
                      "rmDefParams": True}

        try:
            if not parent.isValid():
                self.newPackWithDialog()
            elif name in Package.addableAttrs():
                self.addItemWithDialog(objType=ClassesInfo.addType(Package, name), **kwargs)
            elif ClassesInfo.addType(type(parentObj)):
                self.addItemWithDialog(objType=ClassesInfo.addType(type(parentObj)), **kwargs)
            else:
                raise TypeError("Parent type is not extendable:", type(parent.data(OBJECT_ROLE)))
        except Exception as e:
            print(e)
            QMessageBox.critical(self, "Error", str(e))

    def addItemWithDialog(self, parent: QModelIndex, objType, objVal=None,
                          title="", rmDefParams=False):
        if objType is Package:
            self.newPackWithDialog()
            return
        elif objType is StoredFile:
            self.addFileWithDialog(parent)
            return
        super(PackTreeView, self).addItemWithDialog(parent, objType, objVal, title, rmDefParams)

    def newPackWithDialog(self):
        saved = False
        file = 'new_aas_file.aasx'

        while not saved:
            file = QFileDialog.getSaveFileName(self, 'Create new AAS File', file,
                                               filter=FILTER_AAS_FILES,
                                               initialFilter=self.defNewFileTypeFilter,
                                               options=FILE_DIALOG_OPTIONS)[0]
            if file:
                pack = Package()
                saved = self.savePack(pack, file)
                if saved:
                    self.model().setData(QModelIndex(), pack, ADD_ITEM_ROLE)
            else:
                # cancel pressed
                return

    def openPackWithDialog(self):
        opened = False
        file = ""
        while not opened:
            file = QFileDialog.getOpenFileName(self, "Open AAS file", file,
                                               filter=FILTER_AAS_FILES,
                                               options=FILE_DIALOG_OPTIONS)[0]
            if file:
                opened = self.openPack(file)
            else:
                # cancel pressed
                return

    def addFileWithDialog(self, parent: QModelIndex):
        opened = False
        file = ""
        while not opened:
            file = QFileDialog.getOpenFileName(self, "Add file", file,
                                               options=FILE_DIALOG_OPTIONS)[0]
            if file:
                storedFile = StoredFile(filePath=file)
                opened = self.model().setData(parent, storedFile, ADD_ITEM_ROLE)
            else:
                # cancel pressed
                return

    def openPack(self, file: str) -> bool:
        try:
            pack = Package(file)
            absFile = pack.file.absolute().as_posix()
            self.updateRecentFiles(absFile)
        except Exception as e:
            self.removeFromRecentFiles(file)
            QMessageBox.critical(self, "Error", f"Package {file} couldn't be opened: {e}")
        else:
            openedPacks = self.model().data(QModelIndex(), OPENED_FILES_ROLE)
            if Path(file).absolute() in openedPacks:
                QMessageBox.critical(self, "Error", f"Package {file} is already opened")
            else:
                self.model().setData(QModelIndex(), pack, ADD_ITEM_ROLE)
                return True
        return False

    def savePack(self, pack: Package = None, file: str = None) -> bool:
        pack = self.currentIndex().data(PACKAGE_ROLE) if pack is None else pack
        try:
            pack.write(file)
            self.updateRecentFiles(pack.file.absolute().as_posix())
            return True
        except (TypeError, ValueError) as e:
            QMessageBox.critical(self, "Error", f"Package couldn't be saved: {file}: {e}")
        except AttributeError as e:
            QMessageBox.critical(self, "Error", f"No chosen package to save: {e}")
        return False

    def savePackAsWithDialog(self, pack: Package = None) -> bool:
        pack = self.currentIndex().data(PACKAGE_ROLE) if pack is None else pack
        saved = False
        file = pack.file.as_posix()
        while not saved:
            try:
                file = QFileDialog.getSaveFileName(self, 'Save AAS File', file,
                                                   filter=FILTER_AAS_FILES,
                                                   options=FILE_DIALOG_OPTIONS)[0]
            except AttributeError as e:
                QMessageBox.critical(self, "Error", f"No chosen package to save: {e}")
            else:
                if file:
                    saved = self.savePack(pack, file)
                else:
                    # cancel pressed
                    return

    def saveAll(self):
        for pack in self.model().data(QModelIndex(), OPENED_PACKS_ROLE):
            self.savePack(pack)

    def closeFileWithDialog(self):
        pack = self.currentIndex().data(PACKAGE_ROLE)
        try:
            packItem, = self.model().match(QModelIndex(), OBJECT_ROLE, pack, hits=1)
        except ValueError:
            QMessageBox.critical(self, "Not found error",
                                 f"The file to close is not found: {pack}")
        if packItem.isValid():
            try:
                dialog = QMessageBox(QMessageBox.NoIcon, f"Close {pack}",
                                     f"Do you want to save your changes in {pack} before closing?",
                                     standardButtons=QMessageBox.Save |
                                                     QMessageBox.Cancel |
                                                     QMessageBox.Discard)
                dialog.setDefaultButton=QMessageBox.Save
                dialog.button(QMessageBox.Save).setText("&Save&Close")
                res = dialog.exec()
                if res == QMessageBox.Save:
                    self.savePack()
                    self.closeFile(packItem)
                elif res == QMessageBox.Discard:
                    self.closeFile(packItem)
            except AttributeError as e:
                QMessageBox.critical(self, "Error", f"No chosen package to close: {e}")

    def closeAllFilesWithDialog(self):
        dialog = QMessageBox(QMessageBox.NoIcon, f"Close all AAS files",
                             f"Do you want to save your changes before closing? ",
                             standardButtons=QMessageBox.Save |
                                             QMessageBox.Cancel |
                                             QMessageBox.Discard)
        dialog.setDefaultButton=QMessageBox.Save
        dialog.button(QMessageBox.Save).setText("&Save and Close All")
        res = dialog.exec()
        if res == QMessageBox.Save:
            for pack in self.model().data(QModelIndex(), OPENED_PACKS_ROLE):
                self.savePack(pack)
                packItem, = self.model().match(QModelIndex(), OBJECT_ROLE, pack, hits=1)
                self.closeFile(packItem)
        elif res == QMessageBox.Discard:
            for pack in self.model().data(QModelIndex(), OPENED_PACKS_ROLE):
                packItem, = self.model().match(QModelIndex(), OBJECT_ROLE, pack, hits=1)
                self.closeFile(packItem)

    def closeFile(self, packItem: QModelIndex):
        self.model().setData(packItem, NOT_GIVEN, CLEAR_ROW_ROLE)

    def openRecentSlot(self):
        action = self.sender()
        if action:
            self.openPack(action.data())

    def updateRecentFiles(self, file: str):
        self.removeFromRecentFiles(file)
        settings = QSettings(ACPLT, APPLICATION_NAME)
        files = settings.value('recentFiles', [])
        files.insert(0, file)
        del files[MAX_RECENT_FILES:]
        settings.setValue('recentFiles', files)

    def removeFromRecentFiles(self, file: str):
        settings = QSettings(ACPLT, APPLICATION_NAME)
        files = settings.value('recentFiles', [])
        try:
            files.remove(file)
        except ValueError:
            pass
        except AttributeError:
            files = []
        settings.setValue('recentFiles', files)

    def updateRecentFileActs(self):
        settings = QSettings(ACPLT, APPLICATION_NAME)
        files = settings.value('recentFiles', [])
        try:
            files = files[:MAX_RECENT_FILES]
        except TypeError:
            files = []

        for i, file in enumerate(files):
            if len(file) < 30:
                self.recentFileActs[i].setText(file)
            else:
                self.recentFileActs[i].setText(f"..{file[len(file)-30:]}")
            self.recentFileActs[i].setData(file)
            self.recentFileActs[i].setVisible(True)

        for i in range(len(files), MAX_RECENT_FILES):
            self.recentFileActs[i].setVisible(False)

        self.recentFilesSeparator.setVisible(bool(files))

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls:
            event.accept()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()

    def dropEvent(self, e: QDropEvent) -> None:
        for url in e.mimeData().urls():
            file = str(url.toLocalFile())
            self.openPack(file)
