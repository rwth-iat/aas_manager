#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
import copy
import logging
import typing
from pathlib import Path
from typing import Optional

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QModelIndex, QSettings, QPoint
from PyQt5.QtGui import QDropEvent, QDragEnterEvent, QKeyEvent
from PyQt5.QtWidgets import QAction, QMessageBox, QFileDialog, QMenu, QWidget, QDialog
from basyx.aas.adapter import aasx
from basyx.aas.adapter.aasx import DictSupplementaryFileContainer
from basyx.aas.model import AssetAdministrationShell, DictObjectStore, Submodel

from aas_editor.delegates import EditDelegate
from aas_editor.package import Package, StoredFile
from aas_editor.settings import FILTER_AAS_FILES, CLASSES_INFO, PACKVIEW_ATTRS_INFO, \
    FILE_TYPE_FILTERS, NOT_GIVEN, REFERABLE_INHERITORS_ATTRS
from aas_editor.settings.app_settings import NAME_ROLE, OBJECT_ROLE, PACKAGE_ROLE, MAX_RECENT_FILES, ACPLT, \
    APPLICATION_NAME, OPENED_PACKS_ROLE, OPENED_FILES_ROLE, ADD_ITEM_ROLE, \
    TYPE_ROLE, \
    CLEAR_ROW_ROLE, AppSettings, COLUMN_NAME_ROLE, OBJECT_COLUMN_NAME, OBJECT_VALUE_COLUMN_NAME
from aas_editor.settings.shortcuts import SC_OPEN, SC_SAVE_ALL
from aas_editor.settings.icons import NEW_PACK_ICON, OPEN_ICON, OPEN_DRAG_ICON, SAVE_ICON, SAVE_ALL_ICON, \
    VIEW_ICON, ADD_ICON
from aas_editor.utils import util_type
from aas_editor.utils.util import getDefaultVal, getReqParams4init
from aas_editor.utils.util_classes import ClassesInfo
from aas_editor.widgets import TreeView
from aas_editor.widgets.treeview import HeaderView
from aas_editor import dialogs


class PackHeaderView(HeaderView):
    def __init__(self, orientation, parent: Optional[QWidget] = ...) -> None:
        self.customLists = {}
        super(PackHeaderView, self).__init__(orientation, parent)

    def setCustomLists(self, value: typing.Dict["str", typing.List[str]]):
        self.customLists = value
        self.initMenu()

    def initMenu(self) -> None:
        self.menu = QMenu(self)

        allColumnsMenu = self.menu.addMenu("All Columns")
        for i in self.actions():
            allColumnsMenu.addAction(i)

        showColumns4typeMenu = self.menu.addMenu("Show Columns for type")
        for cls in REFERABLE_INHERITORS_ATTRS:
            clsname = util_type.getTypeName(cls)
            sectionNames = REFERABLE_INHERITORS_ATTRS[cls]
            showColumnsAct = QAction(f"{clsname}", self,
                                     toolTip=f"Show attributes of Type: {clsname}",
                                     statusTip=f"Show attributes of Type: {clsname}",
                                     triggered=lambda: self.onShowListOfSectionsAct())
            showColumnsAct.setData(sectionNames)
            showColumns4typeMenu.addAction(showColumnsAct)

        showColumnsListMenu = self.menu.addMenu("Show custom column list")
        showColumnsListMenu.setToolTip("To manage custom lists, edit custom_column_lists.json")
        for listname in self.customLists:
            sectionNames = self.customLists[listname]
            showColumnsAct = QAction(f"{listname}", self,
                                     toolTip=f"Show custom list {listname}: {sectionNames}. To manage custom lists, edit custom_column_lists.json",
                                     statusTip=f"Show custom list {listname}: {sectionNames}. To manage custom lists, edit custom_column_lists.json",
                                     triggered=lambda: self.onShowListOfSectionsAct())
            showColumnsAct.setData(sectionNames)
            showColumnsListMenu.addAction(showColumnsAct)

        self.menu.addSeparator()
        unchooseAllAct = QAction("Hide all columns", self,
                                 toolTip="Hide all columns",
                                 statusTip="Hide all columns",
                                 triggered=lambda: self.hideAllSections())
        self.menu.addAction(unchooseAllAct)

    def onShowListOfSectionsAct(self):
        action: QAction = self.sender()
        sectionNames = action.data()
        self.showSectionWithNames(sectionNames, only=True)

    def openMenu(self, point: QPoint):
        chosenSection = self.logicalIndexAt(point)
        hideChosenSection = QAction(f"Hide column", self,
                                    toolTip=f"Hide column",
                                    statusTip=f"Hide column",
                                    triggered=lambda: self.hideSection(chosenSection))
        self.menu.addAction(hideChosenSection)
        self.menu.exec_(self.viewport().mapToGlobal(point))
        self.menu.removeAction(hideChosenSection)


class PackTreeView(TreeView):
    EMPTY_VIEW_MSG = "Drop AAS files here"
    EMPTY_VIEW_ICON = OPEN_DRAG_ICON

    def __init__(self, parent=None, **kwargs):
        self.filesObjStores = dict()
        self.scanFolderForExistFiles()
        super(PackTreeView, self).__init__(parent,
                                           emptyViewMsg=self.EMPTY_VIEW_MSG,
                                           emptyViewIcon=self.EMPTY_VIEW_ICON, **kwargs)
        PackTreeView.__instance = self
        self.recentFilesSeparator = None
        self.setAcceptDrops(True)
        self.setExpandsOnDoubleClick(False)
        self.setSelectionBehavior(self.SelectItems)
        self.setHeader(PackHeaderView(Qt.Horizontal, self))

    # Scan the folder "aas_files" and creat a dict filesObjStores of DictObjectStore elements and its names
    def scanFolderForExistFiles(self):
        path = Path.cwd()
        path = path / 'aas_files'

        if not path.is_dir():
            path.mkdir()

        aasxFiles = [file for file in path.rglob('*.aasx')]
        xmlFiles = [file for file in path.rglob('*.xml')]
        jsonFiles = [file for file in path.rglob('*.json')]
        files = aasxFiles + xmlFiles + jsonFiles

        # Read the aasx file and store it in DictObjectStore in dictionary fileObjDict.
        for file in files:
            try:
                fileType = file.suffix.lower().strip()
                if fileType == ".xml":
                    objStore = aasx.read_aas_xml_file(file.as_posix())
                elif fileType == ".json":
                    with open(file, "r") as f:  # TODO change if aas changes
                        objStore = aasx.read_aas_json_file(f)
                elif fileType == ".aasx":
                    objStore = DictObjectStore()
                    fileStore = DictSupplementaryFileContainer()  # prosto tak
                    reader = aasx.AASXReader(file.as_posix())
                    reader.read_into(objStore, fileStore)
                else:
                    raise TypeError("Wrong file type:", self.file.suffix)
                self.filesObjStores[file.name] = objStore
            except Exception as e:
                # If a package is with an error, that file will be skipped.
                logging.exception(f"Error while reading {file}: {e}. Submodels can not be read")

    @property
    def defaultNewFileTypeFilter(self):
        return AppSettings.DEFAULT_NEW_FILETYPE_FILTER.value()

    @defaultNewFileTypeFilter.setter
    def defaultNewFileTypeFilter(self, value):
        AppSettings.DEFAULT_NEW_FILETYPE_FILTER.setValue(value)

    # noinspection PyArgumentList
    def initActions(self):
        super(PackTreeView, self).initActions()
        self.addAct.setText("Add package")
        self.addAct.setEnabled(True)

        self.newPackAct = QAction(NEW_PACK_ICON, "&New AAS file", self,
                                  statusTip="Create new AAS file",
                                  triggered=lambda: self.newPackWithDialog(),
                                  enabled=True)

        self.openPackAct = QAction(OPEN_ICON, "&Open AAS file", self,
                                   shortcut=SC_OPEN,
                                   statusTip="Open AAS file",
                                   triggered=lambda: self.openPackWithDialog(),
                                   enabled=True)

        # Recent files actions
        self.recentFileActs = []
        for i in range(MAX_RECENT_FILES):
            recentFileAct = QAction("", self,
                                    statusTip=f"Open recent file",
                                    triggered=lambda: self.openRecentSlot(),
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
                                  triggered=lambda: self.saveAll(),
                                  enabled=True)

        self.closeAct = QAction("Close AAS file", self,
                                statusTip="Close current file",
                                triggered=lambda: self.closeFileWithDialog(),
                                enabled=False)

        self.closeAllAct = QAction("Close all", self,
                                   statusTip="Close all files",
                                   triggered=lambda: self.closeAllFilesWithDialog(),
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

        self.dictCopyExistSubmodelActs = self.initDictCopyExistSubmodelActs()

        self.autoScrollFromSrcAct.toggle()

        self.shellViewAct = QAction(VIEW_ICON, "Shell view", self,
                                    toolTip="Shell view",
                                    statusTip="Change to shell view",
                                    triggered=lambda: self.onShellViewPushed(),
                                    checkable=True)

        self.setItemDelegate(EditDelegate(self))

    def initDictCopyExistSubmodelActs(self):
        dictCopyExistSubmodelActs = {}  # {"file1": list(QAction_copySubmodel1, QAction_copySubmodel2, ...)}
        # filesObjStores contains packages and its instances
        for file, objStore in self.filesObjStores.items():
            copyExistSubmodelActs = []
            for obj in objStore:
                if isinstance(obj, Submodel):
                    if not obj.id_short == "":
                        name = obj.id_short
                    else:
                        name = obj.identification.id
                    existSubmodelAct = QAction(name, self,
                                               statusTip=f"Copy existing submodel in current package",
                                               triggered=lambda: self.onAddExistingSubmodelPushed())
                    existSubmodelAct.setData(obj)
                    copyExistSubmodelActs.append(existSubmodelAct)
            dictCopyExistSubmodelActs[file] = copyExistSubmodelActs
        return dictCopyExistSubmodelActs

    def onAddExistingSubmodelPushed(self):
        action = self.sender()
        if action:
            submodel = copy.deepcopy(action.data())
            self.treeObjClipboard.clear()
            self.treeObjClipboard.append(submodel)
            self.pasteAct.trigger()

    def onEditCreate(self, objVal=None, index=QModelIndex()) -> bool:
        """
        :param objVal: value to set in dialog input widgets
        :raise KeyError if no typehint found and no objVal was given
        """
        if not index.isValid():
            index = self.currentIndex()
        if index.isValid():
            objVal = objVal if objVal else index.data(Qt.EditRole)
            return self._onEditCreate(objVal, index)

    def _onEditCreate(self, objVal, index) -> bool:
        attribute = index.data(COLUMN_NAME_ROLE)
        parentObj = index.data(OBJECT_ROLE)
        try:
            if attribute == OBJECT_COLUMN_NAME:
                attrTypeHint = type(parentObj)
            else:
                attrTypeHint = util_type.getAttrTypeHint(type(parentObj), attribute)
        except KeyError as e:
            if objVal:
                attrTypeHint = type(objVal)
            else:
                raise KeyError("No typehint found for the given item", attribute)
        return self.replItemWithDialog(index, attrTypeHint, title=f"Edit/Create {attribute}", objVal=objVal)

    def toggleDefNewFileType(self):
        # FIXME refactor
        action = self.sender()
        if action:
            typ = action.text()
            self.defaultNewFileTypeFilter = FILE_TYPE_FILTERS[typ]

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
        self.initMenuAddExistingSubmodels()
        # self.attrsMenu.insertAction(self.addAct, self.addExistingSubmodelsAct)

        self.openInCurrTabAct.triggered.connect(
            lambda: self.openInCurrTabClicked.emit(self.currentIndex()))
        self.openInNewTabAct.triggered.connect(
            lambda: self.openInNewTabClicked.emit(self.currentIndex()))
        self.openInBackgroundAct.triggered.connect(
            lambda: self.openInBgTabClicked.emit(self.currentIndex()))
        self.openInNewWindowAct.triggered.connect(
            lambda: self.openInNewWindowClicked.emit(self.currentIndex()))

    # Create Menu for adding existing submodels.
    def initMenuAddExistingSubmodels(self):
        self.addExistSubmodelsMenu = QMenu("Add existing submodel", self.attrsMenu)
        self.addExistSubmodelsMenu.setIcon(ADD_ICON)
        self.addExistSubmodelsMenu.menuAction().setEnabled(False)
        # Add menu with a name of model.
        # dictCopyExistSubmodelActs contains the package names and the list of QActions of its submodels.
        for filename, copyPasteSubmodelActs in self.dictCopyExistSubmodelActs.items():
            nameMenu = self.addExistSubmodelsMenu.addMenu(filename)
            # In copyPasteSubmodelActs are QActions with submodels
            for copyPasteSubmodelAct in copyPasteSubmodelActs:
                nameMenu.addAction(copyPasteSubmodelAct)
        self.attrsMenu.insertMenu(self.addAct, self.addExistSubmodelsMenu)

    # This function makes the 'Add existing submodel' menu visible only if the 'submodel' element is clicked.
    def updateCopyPasteSubmodelActs(self, index: QModelIndex):
        attrName = index.data(NAME_ROLE)
        if attrName == "submodels":
            self.addExistSubmodelsMenu.menuAction().setEnabled(True)
        else:
            self.addExistSubmodelsMenu.menuAction().setEnabled(False)

    def updateActions(self, index: QModelIndex):
        super(PackTreeView, self).updateActions(index)
        self.updateCopyPasteSubmodelActs(index)

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

    def updateAddAct(self, index: QModelIndex):
        super().updateAddAct(index)

        attrName = index.data(NAME_ROLE)
        if attrName in Package.addableAttrs():
            addActText = ClassesInfo.addActText(Package, attrName)
            self.addAct.setEnabled(True)
            self.addAct.setText(addActText)

        # update add action
        if not index.isValid():
            self.addAct.setEnabled(True)
            self.addAct.setText("Add package")

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
                      "objVal": objVal}
        else:
            kwargs = {"parent": parent}

        try:
            if not parent.isValid():
                self.newPackWithDialog()
            elif name in Package.addableAttrs():
                self.addItemWithDialog(objTypeHint=ClassesInfo.addType(Package, name), **kwargs)
            elif ClassesInfo.addType(type(parentObj)):
                self.addItemWithDialog(objTypeHint=ClassesInfo.addType(type(parentObj)), **kwargs)
            else:
                raise TypeError("Parent type is not extendable:", type(parent.data(OBJECT_ROLE)))
        except Exception as e:
            dialogs.ErrorMessageBox.withTraceback(self, str(e)).exec()

    def addItemWithDialog(self, parent: QModelIndex, objTypeHint, objVal=None,
                          title="", rmDefParams=False, **kwargs):
        if objTypeHint is Package:
            self.newPackWithDialog()
            return
        elif objTypeHint is StoredFile:
            self.addFileWithDialog(parent)
            return
        super(PackTreeView, self).addItemWithDialog(parent, objTypeHint, objVal, title, rmDefParams, **kwargs)

    def newPackWithDialog(self, filter=FILTER_AAS_FILES):
        saved = False
        file = 'new_aas_file.aasx'

        while not saved:
            file, _ = QFileDialog.getSaveFileName(self, 'Create new AAS File', file,
                                                  filter=filter,
                                                  initialFilter=self.defaultNewFileTypeFilter)
            if file:
                pack = Package()
                saved = self.savePack(pack, file)
                if saved:
                    self.model().setData(QModelIndex(), pack, ADD_ITEM_ROLE)
            else:
                # cancel pressed
                return

    def openPackWithDialog(self, filter=FILTER_AAS_FILES):
        opened = False
        file = ""
        while not opened:
            file, _ = QFileDialog.getOpenFileName(self, "Open AAS file", file,
                                                  filter=filter)
            if file:
                opened = self.openPack(file)
            else:
                # cancel pressed
                return

    def addFileWithDialog(self, parent: QModelIndex):
        opened = False
        file = ""
        while not opened:
            file, _ = QFileDialog.getOpenFileName(self, "Add file", file)
            if file:
                storedFile = StoredFile(filePath=file)
                opened = self._setItemData(parent, storedFile, ADD_ITEM_ROLE)
            else:
                # cancel pressed
                return

    def openPack(self, file: str) -> typing.Union[bool, Package]:
        try:
            try:
                pack = Package(file, failsafe=False)
            except Exception as e:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Warning)
                msgBox.setText(f"Error while reading package:\n{file}")
                msgBox.setInformativeText("Do you still want to open it?\nSome objects may be missing or incorrect.")
                msgBox.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes)
                msgBox.setDefaultButton(QMessageBox.Yes)
                msgBox.setDetailedText(f"{e}")
                ret = msgBox.exec()
                if ret == QMessageBox.Yes:
                    pack = Package(file, failsafe=True)
                else:
                    return False
            absFile = pack.file.absolute().as_posix()
            self.updateRecentFiles(absFile)
        except Exception as e:
            self.removeFromRecentFiles(file)
            dialogs.ErrorMessageBox.withTraceback(self, f"Package {file} couldn't be opened: {e}").exec()
        else:
            openedPacks = self.model().data(QModelIndex(), OPENED_FILES_ROLE)
            if Path(file).absolute() in openedPacks:
                QMessageBox.critical(self, "Error", f"Package {file} is already opened")
            else:
                self.model().setData(QModelIndex(), pack, ADD_ITEM_ROLE)
                return pack
        return False

    def savePack(self, pack: Package = None, file: str = None) -> bool:
        pack = self.currentIndex().data(PACKAGE_ROLE) if pack is None else pack
        try:
            pack.write(file)
            self.updateRecentFiles(pack.file.absolute().as_posix())
            if self.model().rowCount(QModelIndex()) == 1:
                self.setWindowModified(False)
            return True
        except (TypeError, ValueError, KeyError) as e:
            dialogs.ErrorMessageBox.withTraceback(self, f"Package couldn't be saved: {file}: {e}").exec()
        except AttributeError as e:
            dialogs.ErrorMessageBox.withTraceback(self, f"No chosen package to save: {e}").exec()
        return False

    def savePackAsWithDialog(self, pack: Package = None, filter=FILTER_AAS_FILES) -> bool:
        pack = self.currentIndex().data(PACKAGE_ROLE) if pack is None else pack
        saved = False
        file = pack.file.as_posix()
        while not saved:
            try:
                file, _ = QFileDialog.getSaveFileName(self, 'Save AAS File', file,
                                                      filter=filter)
            except AttributeError as e:
                dialogs.ErrorMessageBox.withTraceback(self, f"No chosen package to save: {e}").exec()
            else:
                if file:
                    saved = self.savePack(pack, file)
                else:
                    # cancel pressed
                    return

    def saveAll(self):
        saved = [self.savePack(pack) for pack in self.model().data(QModelIndex(), OPENED_PACKS_ROLE)]
        if all(saved):
            self.setWindowModified(False)

    def closeFileWithDialog(self):
        pack = self.currentIndex().data(PACKAGE_ROLE)
        try:
            packItem, = self.model().match(QModelIndex(), OBJECT_ROLE, pack, hits=1)
        except ValueError:
            QMessageBox.critical(self, "Not found error",
                                 f"The file to close is not found: {pack}")
            return

        if packItem.isValid():
            try:
                dialog = QMessageBox(QMessageBox.NoIcon, f"Close {pack}",
                                     f"Do you want to save your changes in {pack} before closing?",
                                     standardButtons=QMessageBox.Save |
                                                     QMessageBox.Cancel |
                                                     QMessageBox.Discard)
                dialog.setDefaultButton = QMessageBox.Save
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
        dialog.setDefaultButton = QMessageBox.Save
        dialog.button(QMessageBox.Save).setText("&Save and Close All")
        res = dialog.exec()
        if res == QMessageBox.Save:
            for pack in self.model().data(QModelIndex(), OPENED_PACKS_ROLE):
                self.savePack(pack)
            self.closeAllFiles()
        elif res == QMessageBox.Discard:
            self.closeAllFiles()

    def closeAllFiles(self):
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
                self.recentFileActs[i].setText(f"..{file[len(file) - 30:]}")
            self.recentFileActs[i].setData(file)
            self.recentFileActs[i].setVisible(True)

        for i in range(len(files), MAX_RECENT_FILES):
            self.recentFileActs[i].setVisible(False)

        self.recentFilesSeparator.setVisible(bool(files))

    def collapse(self, index: QtCore.QModelIndex) -> None:
        newIndex = index.siblingAtColumn(0)
        if not self.isExpanded(index) or not index.child(0, 0).isValid():
            if newIndex.parent() != self.rootIndex():
                newIndex = newIndex.parent()
        self.setCurrentIndex(newIndex)
        super(PackTreeView, self).collapse(newIndex)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key_Right, Qt.Key_Left):
            self.setFocus()
            currIndex = self.currentIndex()
            if event.key() == Qt.Key_Right:
                self.navigate2nextEnabledItemInRow(currIndex)
            else:
                self.navigate2nextEnabledItemInRow(currIndex, leftDirection=True)
        else:
            super(PackTreeView, self).keyPressEvent(event)

    def navigate2nextEnabledItemInRow(self, index: QModelIndex, leftDirection=False):
        delta = -1 if leftDirection else +1
        currCol = index.column()
        if index.isValid():
            visCol = self.header().visualIndex(currCol)
            i = delta
            while True:
                newLogCol = self.header().logicalIndex(visCol + i)
                nextItem = index.siblingAtColumn(newLogCol)
                if visCol + i < 0 or visCol + i >= self.header().count():
                    break
                if not self.header().isSectionHidden(newLogCol) and nextItem.flags() & Qt.ItemIsEnabled:
                    self.setCurrentIndex(index.siblingAtColumn(newLogCol))
                    break
                i += delta

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

    def onDelClear(self):
        index = self.currentIndex()
        attribute = index.data(COLUMN_NAME_ROLE)
        if isinstance(index.data(OBJECT_ROLE), Package):
            self.closeAct.trigger()
        elif attribute in (OBJECT_COLUMN_NAME, OBJECT_VALUE_COLUMN_NAME):
            super(PackTreeView, self).onDelClear()
        else:
            parentObjType = type(index.data(OBJECT_ROLE))
            defaultVal = getDefaultVal(parentObjType, attribute)
            self._setItemData(index, defaultVal, Qt.EditRole)

    def isPasteOk(self, index: QModelIndex) -> bool:
        attrName = index.data(COLUMN_NAME_ROLE)
        if attrName in (OBJECT_COLUMN_NAME, OBJECT_VALUE_COLUMN_NAME):
            return super(PackTreeView, self).isPasteOk(index)
        else:
            if not self.treeObjClipboard or not index.isValid():
                return False

            try:
                attrTypehint = util_type.getAttrTypeHint(type(index.data(OBJECT_ROLE)), attrName, delOptional=False)
            except KeyError as e:
                logging.exception(e)
                # print(e)
                return False

            obj2paste = self.treeObjClipboard[0]
            targetTypeHint = attrTypehint

            try:
                if util_type.checkType(obj2paste, targetTypeHint):
                    return True
            except (AttributeError, TypeError) as e:
                logging.exception(e)
                # print(e)
            return False

    def onPaste(self):
        index = self.currentIndex()
        attrName = index.data(COLUMN_NAME_ROLE)
        if attrName in (OBJECT_COLUMN_NAME, OBJECT_VALUE_COLUMN_NAME):
            super(PackTreeView, self).onPaste()
        else:
            obj2paste = self.treeObjClipboard[0]
            targetParentObj = index.data(OBJECT_ROLE)
            targetTypeHint = util_type.getAttrTypeHint(type(index.data(OBJECT_ROLE)), attrName, delOptional=False)
            reqAttrsDict = getReqParams4init(type(obj2paste), rmDefParams=True)

            # if no req. attrs, paste data without dialog
            # else paste data with dialog for asking to check req. attrs
            if util_type.checkType(obj2paste, targetTypeHint):
                self._onPasteReplace(index, obj2paste, withDialog=bool(reqAttrsDict))
