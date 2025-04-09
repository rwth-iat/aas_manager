#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/

import copy
import json
import logging
import traceback
import typing
from functools import partial
from pathlib import Path
from typing import Optional

from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QModelIndex, QSettings, QPoint
from PyQt6.QtGui import QDropEvent, QDragEnterEvent, QKeyEvent, QClipboard, QAction
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QMenu, QWidget, QApplication
from basyx.aas.adapter.aasx import AASXReader, DictSupplementaryFileContainer
from basyx.aas.adapter.json import read_aas_json_file, AASToJsonEncoder
from basyx.aas.adapter.xml import read_aas_xml_file
from basyx.aas.model import SetObjectStore, Submodel

from aas_editor.delegates import EditDelegate
from aas_editor.package import Package, StoredFile
from aas_editor.settings import FILTER_AAS_FILES, AAS_FILE_TYPE_FILTERS, NOT_GIVEN, REFERABLE_INHERITORS_ATTRS
from aas_editor.settings.app_settings import NAME_ROLE, OBJECT_ROLE, PACKAGE_ROLE, \
    MAX_RECENT_FILES, OPENED_PACKS_ROLE, OPENED_FILES_ROLE, ADD_ITEM_ROLE, \
    CLEAR_ROW_ROLE, AppSettings, COLUMN_NAME_ROLE, OBJECT_COLUMN_NAME, \
    OBJECT_VALUE_COLUMN_NAME, DEFAULT_COLUMNS_IN_PACKS_TABLE_TO_SHOW, COPY_ROLE
from aas_editor.settings.shortcuts import SC_OPEN, SC_SAVE_ALL
from aas_editor.settings.icons import NEW_PACK_ICON, OPEN_ICON, OPEN_DRAG_ICON, SAVE_ICON, SAVE_ALL_ICON, ADD_ICON
from aas_editor.utils import util_type
from aas_editor.utils.util import getDefaultVal, getReqParams4init
from aas_editor.utils.util_classes import ClassesInfo
from aas_editor.widgets import TreeView
from aas_editor.widgets.treeview import HeaderView
from aas_editor import dialogs
from settings import AAS_FILE_TYPES, APPLICATION_NAME, IAT


SUBMODEL_TEMPLATES_FOLDER = 'submodel_templates'


class PackHeaderView(HeaderView):
    def __init__(self, orientation, parent: Optional[QWidget] = ...) -> None:
        self.customLists = {}
        super(PackHeaderView, self).__init__(orientation, parent)

    def setCustomLists(self, value: typing.Dict["str", typing.List[str]]):
        self.customLists = value
        self.initMenu()

    def initMenu(self) -> None:
        self.menu = QMenu("Columns", self)

        showBasicColumnsAct = QAction("Show Basic Columns", self,
                                      triggered=lambda: self.showSectionWithNames(DEFAULT_COLUMNS_IN_PACKS_TABLE_TO_SHOW, only=True))
        self.menu.addAction(showBasicColumnsAct)

        allColumnsMenu = self.menu.addMenu("Select Columns")
        for i in self.actions():
            allColumnsMenu.addAction(i)

        showColumns4typeMenu = self.menu.addMenu("Show Columns for Attributes of Type")
        for cls in REFERABLE_INHERITORS_ATTRS:
            clsname = util_type.getTypeName(cls)
            sectionNames = REFERABLE_INHERITORS_ATTRS[cls]
            showColumnsAct = QAction(f"{clsname}", self,
                                     toolTip=f"Show attributes of Type: {clsname}",
                                     statusTip=f"Show attributes of Type: {clsname}",
                                     triggered=lambda: self.onShowListOfSectionsAct())
            showColumnsAct.setData(sectionNames)
            showColumns4typeMenu.addAction(showColumnsAct)

        showColumnsFromListMenu = self.menu.addMenu("Show Columns From Custom List")
        menuTip = "To manage custom lists, edit custom_column_lists.json"
        showColumnsFromListMenu.setToolTip(menuTip)
        showColumnsFromListMenu.setStatusTip(menuTip)
        for listname in self.customLists:
            sectionNames = self.customLists[listname]
            showColumnsAct = QAction(f"{listname}", self,
                                     toolTip=f"Show custom list {listname}: {sectionNames}. {menuTip}",
                                     statusTip=f"Show custom list {listname}: {sectionNames}. {menuTip}",
                                     triggered=lambda: self.onShowListOfSectionsAct())
            showColumnsAct.setData(sectionNames)
            showColumnsFromListMenu.addAction(showColumnsAct)

        self.menu.addSeparator()

        showAllColAct = QAction("Show all columns", self,
                                toolTip="Show all columns",
                                statusTip="Show all columns",
                                triggered=lambda: self.showAllSections())
        self.menu.addAction(showAllColAct)

        hideAllColAct = QAction("Hide all columns", self,
                                toolTip="Hide all columns",
                                statusTip="Hide all columns",
                                triggered=lambda: self.hideAllSections())
        self.menu.addAction(hideAllColAct)

        resizeEqualAct = QAction("Resize columns equally", self,
                                 toolTip="Resize columns equally",
                                 statusTip="Resize columns equally",
                                 triggered=lambda: self.resizeSectionsEqual())
        self.menu.addAction(resizeEqualAct)

    def resizeSectionsEqual(self):
        self.resizeSections(HeaderView.ResizeMode.Stretch)
        self.resizeSections(HeaderView.ResizeMode.Interactive)

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
        self.menu.exec(self.viewport().mapToGlobal(point))
        self.menu.removeAction(hideChosenSection)


class PackTreeView(TreeView):
    EMPTY_VIEW_MSG = "Drop AAS files here"
    EMPTY_VIEW_ICON = OPEN_DRAG_ICON

    def __init__(self, parent=None, **kwargs):
        self.copyBufferObjStores = dict()
        self.scanFolderForExistFiles()
        super(PackTreeView, self).__init__(parent,
                                           emptyViewMsg=self.EMPTY_VIEW_MSG,
                                           emptyViewIcon=self.EMPTY_VIEW_ICON, **kwargs)
        PackTreeView.__instance = self
        self.recentFilesSeparator = None
        self.setAcceptDrops(True)
        self.setExpandsOnDoubleClick(False)
        self.setSelectionBehavior(self.SelectionBehavior.SelectItems)
        self.setHeader(PackHeaderView(Qt.Orientation.Horizontal, self))

    # Scan the folder SUBMODEL_TEMPLATES_FOLDER and create a set filesObjStores of SetObjectStore elements and its names
    def scanFolderForExistFiles(self):
        path = Path.cwd()
        path = path / SUBMODEL_TEMPLATES_FOLDER

        if not path.is_dir():
            path.mkdir()

        aasxFiles = [file for file in path.rglob('*.aasx')]
        xmlFiles = [file for file in path.rglob('*.xml')]
        jsonFiles = [file for file in path.rglob('*.json')]
        files = aasxFiles + xmlFiles + jsonFiles

        # Read the aas files and store it in SetObjectStore in dictionary fileObjDict.
        for file in files:
            try:
                fileType = file.suffix.lower().strip()
                if fileType == ".xml":
                    objStore = read_aas_xml_file(file.as_posix())
                elif fileType == ".json":
                    with open(file, "r") as f:  # TODO change if aas changes
                        objStore = read_aas_json_file(f)
                elif fileType == ".aasx":
                    objStore = SetObjectStore()
                    fileStore = DictSupplementaryFileContainer()  # prosto tak
                    reader = AASXReader(file.as_posix())
                    reader.read_into(objStore, fileStore)
                else:
                    raise TypeError("Wrong file type:", self.file.suffix)
                self.copyBufferObjStores[file.name] = objStore
            except Exception as e:
                # If a package is with an error, that file will be skipped.
                logging.exception(f"Error while reading {file}: {e}. Submodels can not be read")

    @property
    def defaultNewFileType(self):
        return AppSettings.DEFAULT_NEW_FILETYPE.value()

    @defaultNewFileType.setter
    def defaultNewFileType(self, value):
        AppSettings.DEFAULT_NEW_FILETYPE.setValue(value)

    # noinspection PyArgumentList
    def initActions(self):
        super(PackTreeView, self).initActions()
        self.addAct.setText("Add package")
        self.addAct.setEnabled(True)

        self.copyJsonAct = QAction("Copy as JSON", self,
                                   statusTip="Copy the object in JSON",
                                   triggered=lambda: self.onJsonCopy(),
                                   enabled=True)

        self.newPackActs = []
        for filetype in AAS_FILE_TYPE_FILTERS:
            newPackAct = QAction(NEW_PACK_ICON, f"New AAS file as {filetype}", self,
                                 statusTip=f"Create new AAS file as {filetype}",
                                 triggered=partial(self.newPackWithDialog, filetype=filetype),
                                 enabled=True)
            self.newPackActs.append(newPackAct)


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

        self.saveInActs = []
        for filetype in AAS_FILE_TYPES:
            saveInAct = QAction(f"Save in {filetype}", self,
                                statusTip=f"Save in {filetype}",
                                triggered=partial(self.savePackInTypeWithDialog, filetype=filetype),
                                enabled=False)
            self.saveInActs.append(saveInAct)

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

        self.existSubmodelCopyActsFromFiles: typing.Dict[str, typing.List[QAction]] = self.initExistSubmodelCopyActsFromFiles()

        self.autoScrollFromSrcAct.toggle()
        self.setItemDelegate(EditDelegate(self))

    def initExistSubmodelCopyActsFromFiles(self):
        existSubmodelCopyActsFromFiles = {}  # {"file1": list(QAction_copySubmodel1, QAction_copySubmodel2, ...)}
        # filesObjStores contains packages and its instances
        for file, objStore in self.copyBufferObjStores.items():
            copyExistSubmodelActs = []
            for obj in objStore:
                if isinstance(obj, Submodel):
                    name = obj.id_short if not obj.id_short == "" else obj.id
                    existSubmodelAct = QAction(name, self,
                                               statusTip=f"Copy existing submodel in current package",
                                               triggered=lambda: self.onAddExistingSubmodelPushed())
                    existSubmodelAct.setData(obj)
                    copyExistSubmodelActs.append(existSubmodelAct)
            existSubmodelCopyActsFromFiles[file] = copyExistSubmodelActs
        return existSubmodelCopyActsFromFiles

    def onAddExistingSubmodelPushed(self):
        action = self.sender()
        if action:
            submodel = copy.deepcopy(action.data())
            self.treeClipboard.clear()
            self.treeClipboard.append(submodel)
            self.pasteAct.trigger()

    def onEditCreate(self, objVal=None, index=QModelIndex()) -> bool:
        """
        :param objVal: value to set in dialog input widgets
        :param index: QModelIndex of the item to edit
        :raise KeyError if no typehint found and no objVal was given
        """
        if not index.isValid():
            index = self.currentIndex()
        if index.isValid():
            objVal = objVal if objVal else index.data(Qt.ItemDataRole.EditRole)
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
            self.defaultNewFileType = AAS_FILE_TYPE_FILTERS[typ]

    # noinspection PyUnresolvedReferences
    def initMenu(self):
        super(PackTreeView, self).initMenu()
        self.attrsMenu.insertAction(self.pasteAct, self.copyJsonAct)

        self.attrsMenu.addSeparator()
        self.attrsMenu.addAction(self.openPackAct)
        self.attrsMenu.addAction(self.saveAct)
        self.attrsMenu.addAction(self.saveAsAct)
        for act in self.saveInActs:
            self.attrsMenu.addAction(act)
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
        for filename, copyPasteSubmodelActs in self.existSubmodelCopyActsFromFiles.items():
            nameMenu = self.addExistSubmodelsMenu.addMenu(filename)
            # In copyPasteSubmodelActs are QActions with submodels
            for copyPasteSubmodelAct in copyPasteSubmodelActs:
                nameMenu.addAction(copyPasteSubmodelAct)
        self.attrsMenu.insertMenu(self.addAct, self.addExistSubmodelsMenu)

    def updateActions(self, index: QModelIndex):
        super(PackTreeView, self).updateActions(index)
        self.updateCopyPasteSubmodelActs(index)
        self.updateOpenInActs(index)
        self.updateSaveActs(index)
        self.updateCloseActs(index)

    def updateCopyPasteSubmodelActs(self, index: QModelIndex):
        """Make the 'Add existing submodel' menu visible if the 'submodel' element is clicked."""
        attrName = index.data(NAME_ROLE)
        self.addExistSubmodelsMenu.menuAction().setEnabled(attrName == "submodels")

    def updateOpenInActs(self, index: QModelIndex):
        if index.isValid():
            for act in self.openInActs:
                act.setEnabled(True)

    def updateSaveActs(self, index: QModelIndex):
        self.saveAct.setEnabled(self.isSaveOk())
        self.saveAct.setText(f"Save {index.data(PACKAGE_ROLE)}")
        self.saveAct.setToolTip(f"Save {index.data(PACKAGE_ROLE)}")
        self.saveAsAct.setEnabled(self.isSaveOk())
        for act in self.saveInActs:
            act.setEnabled(self.isSaveOk())
        self.saveAllAct.setEnabled(self.isSaveAllOk())

    def updateCloseActs(self, index: QModelIndex):
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
        parentParentObj = parent.parent().data(OBJECT_ROLE) if parent.parent().isValid() else None

        if objVal:
            kwargs = {"parent": parent,
                      "objVal": objVal}
        else:
            kwargs = {"parent": parent}

        try:
            if not parent.isValid():
                self.newPackWithDialog()
            elif parentParentObj is not None and ClassesInfo.packViewAttrs(type(parentParentObj)):
                self.addItemWithDialog(objTypeHint=ClassesInfo.addType(type(parentParentObj), name), **kwargs)
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

    def onJsonCopy(self):
        index = self.currentIndex()
        data2copy = index.data(COPY_ROLE)
        json2copy = json.dumps(data2copy, cls=AASToJsonEncoder, indent=2)
        self.treeClipboard.clear()
        self.treeClipboard.append(json2copy, objRepr=json2copy)
        clipboard = QApplication.clipboard()
        clipboard.setText(json2copy, QClipboard.Mode.Clipboard)

    def newPackWithDialog(self, filetype=None, filter=FILTER_AAS_FILES):
        saved = False
        filetype = self.defaultNewFileType if filetype is None else filetype
        file = f'new_aas_file.{filetype}'

        while not saved:
            file, _ = QFileDialog.getSaveFileName(self, 'Create new AAS File', file,
                                                  filter=filter,
                                                  initialFilter=AAS_FILE_TYPE_FILTERS[filetype])
            if file:
                pack = Package()
                saved = self.savePack(pack, file)
                if saved:
                    self.add_pack_to_tree(pack)
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
                msgBox.setIcon(QMessageBox.Icon.Warning)
                msgBox.setText(f"Error while reading package:\n{file}")
                msgBox.setInformativeText(
                    "The file might not align with the official schema. "
                    "Verify with the Tools/compliance tool for specifics. \n\n"
                    "Proceeding may result in missing or incorrect objects. Continue anyway?")
                msgBox.setStandardButtons(QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Yes)
                msgBox.setDefaultButton(QMessageBox.StandardButton.Yes)
                msgBox.setDetailedText(f"{traceback.format_exc()}")
                ret = msgBox.exec()
                if ret == QMessageBox.StandardButton.Yes:
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
                self.add_pack_to_tree(pack)
                return pack
        return False

    def add_pack_to_tree(self, pack: Package):
        self.model().setData(QModelIndex(), pack, ADD_ITEM_ROLE)

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

    def savePackInTypeWithDialog(self, filetype=None, pack: Package = None) -> bool:
        pack = self.currentIndex().data(PACKAGE_ROLE) if pack is None else pack
        file = pack.file.as_posix() if filetype is None else pack.file.with_suffix(f".{filetype}").as_posix()
        self.savePackAsWithDialog(file, pack)

    def savePackAsWithDialog(self, file=None, pack: Package = None, filter=FILTER_AAS_FILES) -> bool:
        pack = self.currentIndex().data(PACKAGE_ROLE) if pack is None else pack
        saved = False
        file = pack.file.as_posix() if file is None else file
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
                if self.isWindowModified():
                    dialog = QMessageBox(QMessageBox.NoIcon, f"Close {pack}",
                                         f"Do you want to save your changes in {pack} before closing?",
                                         standardButtons=QMessageBox.StandardButton.Save |
                                                         QMessageBox.StandardButton.Cancel |
                                                         QMessageBox.StandardButton.Discard)
                    dialog.setDefaultButton = QMessageBox.StandardButton.Save
                    dialog.button(QMessageBox.StandardButton.Save).setText("&Save&Close")
                    res = dialog.exec()
                    if res == QMessageBox.StandardButton.Save:
                        self.savePack()
                    elif res == QMessageBox.StandardButton.Cancel:
                        return
                self.closeFile(packItem)
            except AttributeError as e:
                QMessageBox.critical(self, "Error", f"No chosen package to close: {e}")

    def closeAllFilesWithDialog(self):
        if self.isWindowModified():
            dialog = QMessageBox(QMessageBox.NoIcon, f"Close all AAS files",
                                 f"Do you want to save your changes before closing? ",
                                 standardButtons=QMessageBox.StandardButton.Save |
                                                 QMessageBox.StandardButton.Cancel |
                                                 QMessageBox.StandardButton.Discard)
            dialog.setDefaultButton = QMessageBox.StandardButton.Save
            dialog.button(QMessageBox.StandardButton.Save).setText("&Save and Close All")
            res = dialog.exec()
            if res == QMessageBox.StandardButton.Save:
                for pack in self.model().data(QModelIndex(), OPENED_PACKS_ROLE):
                    self.savePack(pack)
            elif res == QMessageBox.StandardButton.Cancel:
                return
        self.closeAllFiles()

    def closeAllFiles(self):
        for pack in self.model().data(QModelIndex(), OPENED_PACKS_ROLE):
            packItem, = self.model().match(QModelIndex(), OBJECT_ROLE, pack, hits=1)
            self.closeFile(packItem)

    def closeFile(self, packItem: QModelIndex):
        self.model().setData(packItem, NOT_GIVEN, CLEAR_ROW_ROLE)
        if self.model().data(QModelIndex(), OPENED_PACKS_ROLE):
            self.setWindowModified(False)

    def updateRecentFiles(self, file: str):
        self.removeFromRecentFiles(file)
        settings = QSettings(IAT, APPLICATION_NAME)
        files = settings.value('recentFiles', [])
        files.insert(0, file)
        del files[MAX_RECENT_FILES:]
        settings.setValue('recentFiles', files)

    def removeFromRecentFiles(self, file: str):
        settings = QSettings(IAT, APPLICATION_NAME)
        files = settings.value('recentFiles', [])
        try:
            files.remove(file)
        except ValueError:
            pass
        except AttributeError:
            files = []
        settings.setValue('recentFiles', files)

    def updateRecentFileActs(self):
        settings = QSettings(IAT, APPLICATION_NAME)
        files = settings.value('recentFiles', [])
        try:
            files = files[:MAX_RECENT_FILES]
        except TypeError:
            files = []

        for i, file in enumerate(files):
            recentFileAct = self.recentFileActs[i]
            display_text = file if len(file) < 30 else f"..{file[-30:]}"
            recentFileAct.setText(display_text)
            recentFileAct.setVisible(True)
            recentFileAct.triggered.connect(partial(self.openPack, file=file))

        for i in range(len(files), MAX_RECENT_FILES):
            self.recentFileActs[i].setVisible(False)

        self.recentFilesSeparator.setVisible(bool(files))

    def collapse(self, index: QtCore.QModelIndex) -> None:
        newIndex = index.siblingAtColumn(0)
        if not self.isExpanded(index) or not self.model().index(0, 0, index).isValid():
            if newIndex.parent() != self.rootIndex():
                newIndex = newIndex.parent()
        self.setCurrentIndex(newIndex)
        super(PackTreeView, self).collapse(newIndex)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Right, Qt.Key.Key_Left):
            self.setFocus()
            currIndex = self.currentIndex()
            if event.key() == Qt.Key.Key_Right:
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
                if not self.header().isSectionHidden(newLogCol) and nextItem.flags() & Qt.ItemFlag.ItemIsEnabled:
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

    def onOneItemDelClear(self, index: QModelIndex):
        attribute = index.data(COLUMN_NAME_ROLE)
        if isinstance(index.data(OBJECT_ROLE), Package):
            self.closeAct.trigger()
        elif attribute in (OBJECT_COLUMN_NAME, OBJECT_VALUE_COLUMN_NAME):
            super(PackTreeView, self).onOneItemDelClear(index)
        else:
            parentObjType = type(index.data(OBJECT_ROLE))
            defaultVal = getDefaultVal(parentObjType, attribute)
            self._setItemData(index, defaultVal, Qt.ItemDataRole.EditRole)

    def isPasteOk(self, index: QModelIndex) -> bool:
        if self.treeClipboard.isEmpty() or not index.isValid():
            return False

        attrName = index.data(COLUMN_NAME_ROLE)
        if attrName in (OBJECT_COLUMN_NAME, OBJECT_VALUE_COLUMN_NAME):
            return super(PackTreeView, self).isPasteOk(index)

        currObj = index.data(OBJECT_ROLE)
        currObjType = type(currObj)
        try:
            attrTypehint = util_type.getAttrTypeHint(currObjType, attrName, delOptional=False)
        except KeyError as e:
            logging.exception(e)
            return False

        try:
            if util_type.checkType(self.treeClipboard.objForPasteCheck, attrTypehint):
                return True
            if ClassesInfo.addType(currObjType) and isinstance(self.treeClipboard.objForPasteCheck, ClassesInfo.addType(currObjType)):
                return True
        except (AttributeError, TypeError) as e:
            logging.exception(e)
        return False

    def onPaste(self):
        index = self.currentIndex()
        attrName = index.data(COLUMN_NAME_ROLE)
        if attrName in (OBJECT_COLUMN_NAME, OBJECT_VALUE_COLUMN_NAME):
            super(PackTreeView, self).onPaste()
        else:
            obj2paste = self.treeClipboard.objects[-1]
            targetTypeHint = util_type.getAttrTypeHint(type(index.data(OBJECT_ROLE)), attrName, delOptional=False)
            reqAttrsDict = getReqParams4init(type(obj2paste), rmDefParams=True)

            # if no req. attrs, paste data without dialog
            # else paste data with dialog for asking to check req. attrs
            if util_type.checkType(obj2paste, targetTypeHint):
                self._onPasteReplace(index, obj2paste, withDialog=bool(reqAttrsDict))
