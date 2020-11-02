from pathlib import Path

from PyQt5 import QtCore
from PyQt5.QtCore import QModelIndex, QSettings
from PyQt5.QtGui import QDropEvent, QDragEnterEvent
from PyQt5.QtWidgets import QAction, QMessageBox, QFileDialog
from aas.model import Submodel, AssetAdministrationShell, Asset, SubmodelElement

from aas_editor.models import Package, ConceptDescription
from aas_editor.settings import NAME_ROLE, OBJECT_ROLE, PACKAGE_ATTRS, SC_SAVE_ALL, SC_OPEN, \
    PACKAGE_ROLE, MAX_RECENT_FILES, ACPLT, APPLICATION_NAME
from aas_editor.views.treeview import TreeView
import qtawesome as qta


class PackTreeView(TreeView):
    def __init__(self, parent=None):
        super(PackTreeView, self).__init__(parent)
        PackTreeView.__instance = self
        self.recentFilesSeparator = None
        self._upgradeActions()
        self._upgradeMenu()
        self.setAcceptDrops(True)

    # noinspection PyArgumentList
    def _upgradeActions(self):
        self.addAct.setText("Add package")
        self.addAct.setEnabled(True)

        self.newPackAct = QAction(qta.icon("mdi.plus-circle"), "&New AAS file", self,
                                  statusTip="Create new AAS file",
                                  triggered=self.newPackWithDialog,
                                  enabled=True)

        self.openPackAct = QAction(qta.icon("mdi.folder-open"), "&Open AAS file", self,
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

        self.saveAct = QAction(qta.icon("mdi.content-save"), "Save", self,
                               statusTip="Save current file",
                               triggered=lambda: self.savePack(),
                               enabled=False)

        self.saveAsAct = QAction("Save As...", self,
                                 statusTip="Save current file as..",
                                 triggered=lambda: self.savePackAsWithDialog(),
                                 enabled=False)

        self.saveAllAct = QAction(qta.icon("mdi.content-save-all"), "&Save All", self,
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

    # noinspection PyUnresolvedReferences
    def _upgradeMenu(self):
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

    def setModel(self, model: QtCore.QAbstractItemModel) -> None:
        super(PackTreeView, self).setModel(model)
        self.selectionModel().currentChanged.connect(self._updateMenu)

    def _updateMenu(self, index: QModelIndex):
        if index.isValid():
            self.openInCurrTabAct.setEnabled(True)
            self.openInNewTabAct.setEnabled(True)
            self.openInBackgroundAct.setEnabled(True)

        # update save and close actions
        self.saveAct.setEnabled(self._isSaveOk())
        self.saveAsAct.setEnabled(self._isSaveOk())
        self.saveAllAct.setEnabled(self._isSaveAllOk())
        self.closeAct.setEnabled(self._isCloseOk())
        self.closeAllAct.setEnabled(self._isCloseAllOk())

        # update add action
        obj = index.data(OBJECT_ROLE)
        name = index.data(NAME_ROLE)

        # update paste action
        self.pasteAct.setEnabled(self._isPasteOk(index))

        self.addAct.setEnabled(True)
        if isinstance(obj, Package) or not index.isValid():
            self.addAct.setText("Add package")
        elif name in PACKAGE_ATTRS:
            self.addAct.setText(f"Add {name.rstrip('s')}")
        elif isinstance(obj, Submodel):
            self.addAct.setText(f"Add submodel element")
        else:
            self.addAct.setText(f"Add")
            self.addAct.setEnabled(False)

    def _isPasteOk(self, index: QModelIndex) -> bool:
        if not self.treeObjClipboard:
            return False
        else:
            obj2paste = self.treeObjClipboard[0]

        attrName = index.data(NAME_ROLE)
        currObj = index.data(OBJECT_ROLE)

        if isinstance(obj2paste, AssetAdministrationShell):
            if isinstance(currObj, AssetAdministrationShell) or attrName == "shells":
                return True
        elif isinstance(obj2paste, Asset):
            if isinstance(currObj, Asset) or attrName == "assets":
                return True
        elif isinstance(obj2paste, Submodel):
            if isinstance(currObj, Submodel) or attrName == "submodels":
                return True
        elif isinstance(obj2paste, SubmodelElement):
            if isinstance(currObj, SubmodelElement):
                return True
        elif isinstance(obj2paste, ConceptDescription):
            if isinstance(currObj, ConceptDescription) or attrName == "concept_descriptions":
                return True
        return False

    def _isSaveOk(self):
        pack = self.currentIndex().data(PACKAGE_ROLE)
        return True if pack else False

    def _isCloseOk(self):
        pack = self.currentIndex().data(PACKAGE_ROLE)
        return True if pack else False

    def _isSaveAllOk(self):
        return True if self.model().openedPacks() else False

    def _isCloseAllOk(self):
        return True if self.model().openedPacks() else False

    def _addHandler(self, objVal=None, parent: QModelIndex = None):
        parent = parent if parent else self.currentIndex()
        name = parent.data(NAME_ROLE)

        if objVal:
            kwargs = {"parent": parent,
                      "rmDefParams": False,
                      "objVal": objVal}
        else:
            kwargs = {"parent": parent,
                      "rmDefParams": True}

        if isinstance(parent.data(OBJECT_ROLE), Package) or not parent.isValid():
            self.newPackWithDialog()
        elif name == "shells":
            self.addItemWithDialog(objType=AssetAdministrationShell, **kwargs)
        elif name == "assets":
            self.addItemWithDialog(objType=Asset, **kwargs)
        elif name == "submodels":
            self.addItemWithDialog(objType=Submodel, **kwargs)
        elif name == "concept_descriptions":
            self.addItemWithDialog(objType=ConceptDescription, **kwargs)
        elif isinstance(parent.data(OBJECT_ROLE), Submodel):
            self.addItemWithDialog(objType=SubmodelElement, **kwargs)
        else:
            raise TypeError("Parent type is not extendable:", type(parent.data(OBJECT_ROLE)))

    def newPackWithDialog(self):
        file = QFileDialog.getSaveFileName(self, 'Create new AAS File',
                                           filter="AAS files (*.aasx *.xml *.json);;"
                                                  "AASX (*.aasx);; "
                                                  "XML (*.xml);;"
                                                  "JSON (*.json);; All files (*.*)",
                                           options=QFileDialog.DontResolveSymlinks |
                                                   QFileDialog.DontUseNativeDialog
                                           )[0]
        if file:
            pack = Package()
            self.savePack(pack, file)
            self.model().addItem(pack, parent=QModelIndex())

    def openPackWithDialog(self):
        file = QFileDialog.getOpenFileName(self, "Open AAS file",
                                           filter="AAS files (*.aasx *.xml *.json);;"
                                                  "AASX (*.aasx);; "
                                                  "XML (*.xml);;"
                                                  "JSON (*.json);; All files (*.*)",
                                           options=QFileDialog.DontResolveSymlinks |
                                                   QFileDialog.DontUseNativeDialog)[0]
        if file:
            self.openPack(file)

    def openPack(self, file: str):
        try:
            pack = Package(file)
            self.updateRecentFiles(pack.file.absolute().as_posix())
        except (TypeError, ValueError) as e:
            QMessageBox.critical(self, "Error", f"Package {file} couldn't be opened: {e}")
        else:
            if Path(file).absolute() in self.model().openedFiles():
                QMessageBox.critical(self, "Error", f"Package {file} is already opened")
            else:
                self.model().addItem(pack)

    def savePack(self, pack: Package = None, file: str = None):
        pack = self.currentIndex().data(PACKAGE_ROLE) if pack is None else pack
        try:
            pack.write(file)
            self.updateRecentFiles(pack.file.absolute().as_posix())
        except (TypeError, ValueError) as e:
            QMessageBox.critical(self, "Error", f"Package couldn't be saved: {file}: {e}")
        except AttributeError as e:
            QMessageBox.critical(self, "Error", f"No chosen package to save: {e}")

    def savePackAsWithDialog(self, pack: Package = None):
        pack = self.currentIndex().data(PACKAGE_ROLE) if pack is None else pack
        try:
            file = QFileDialog.getSaveFileName(self, 'Save AAS File', pack.file.as_posix(),
                                               filter="AAS files (*.aasx *.xml *.json);;"
                                                      "AASX (*.aasx);; "
                                                      "XML (*.xml);;"
                                                      "JSON (*.json);; All files (*.*)",
                                               options=QFileDialog.DontResolveSymlinks |
                                                       QFileDialog.DontUseNativeDialog
                                               )[0]
        except AttributeError as e:
            QMessageBox.critical(self, "Error", f"No chosen package to save: {e}")
        else:
            self.savePack(pack, file)

    def saveAll(self):
        for pack in self.model().openedPacks():
            self.savePack(pack)

    def closeFileWithDialog(self):
        pack = self.currentIndex().data(PACKAGE_ROLE)
        packItem = self.model().findItemByObj(pack)
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
        else:
            QMessageBox.critical(self, "Not found error",
                                 f"The file to close is not found: {pack}")

    def closeAllFilesWithDialog(self):
        dialog = QMessageBox(QMessageBox.NoIcon, f"Close all AAS files",
                             f"Do you want to save your changes before closing? ",
                             standardButtons=QMessageBox.Save |
                                             QMessageBox.Cancel |
                                             QMessageBox.Discard)
        dialog.setDefaultButton=QMessageBox.Save
        dialog.button(QMessageBox.Save).setText("&Save&Close All")
        res = dialog.exec()
        if res == QMessageBox.Save:
            for pack in self.model().openedPacks():
                self.savePack(pack)
                packItem = self.model().findItemByObj(pack)
                self.closeFile(packItem)
        elif res == QMessageBox.Discard:
            for pack in self.model().openedPacks():
                packItem = self.model().findItemByObj(pack)
                self.closeFile(packItem)

    def closeFile(self, packItem: QModelIndex):
        self.model().removeRow(packItem.row(), packItem.parent())

    def openRecentSlot(self):
        action = self.sender()
        if action:
            self.openPack(action.data())

    def updateRecentFiles(self, file: str):
        settings = QSettings(ACPLT, APPLICATION_NAME)
        files = settings.value('recentFiles', [])
        try:
            files.remove(file)
        except ValueError:
            pass
        files.insert(0, file)
        del files[MAX_RECENT_FILES:]
        settings.setValue('recentFiles', files)

    def updateRecentFileActs(self):
        settings = QSettings(ACPLT, APPLICATION_NAME)
        files = settings.value('recentFiles', [])
        files = files[:MAX_RECENT_FILES]

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
