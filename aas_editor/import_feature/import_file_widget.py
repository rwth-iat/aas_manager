#  Copyright (C) 2022  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFileDialog

from aas_editor.import_feature.import_settings import FILTER_IMPORT_FILES
from aas_editor.import_feature.treeview_import import ImportTreeView
from aas_editor.settings import TOOLBARS_HEIGHT, FILTER_AAS_FILES, JSON_FILES_FILTER
from aas_editor.widgets.lineEdit import LineEdit


class ImportManageWidget(QWidget):
    def __init__(self, parent=None, mainTreeView=None):
        super(ImportManageWidget, self).__init__(parent)
        self.setupLayout()

        self.importFileLine = LineEdit(self, placeholderText="Choose the file to import from")
        self.importFileLine.setReadOnly(True)
        self.chooseFileBtn = QPushButton("Choose file", self, clicked=self.chooseImportFileDialog)
        self.saveMappingBtn = QPushButton("Save mapping", self, clicked=self.saveMappingFileDialog)
        self.useMappingBtn = QPushButton("Use mapping...", self, clicked=self.useMappingFileDialog)
        self.importSettingsBtn = QPushButton("Settings", self)
        self.importBtn = QPushButton("Run Import", self)
        for widget in (self.importFileLine, self.chooseFileBtn, self.saveMappingBtn, self.useMappingBtn, self.importBtn, self.importSettingsBtn):
            self.layout().addWidget(widget)

        self.mainTreeView: ImportTreeView = mainTreeView
        self.importFile: str = ""
        self.fileType: str = ""

    def setTreeView(self, treeview):
        self.mainTreeView = treeview

    def setupLayout(self):
        toolBarHLayout = QHBoxLayout()
        toolBarHLayout.setContentsMargins(5, 0, 5, 0)
        self.setFixedHeight(TOOLBARS_HEIGHT)
        self.setLayout(toolBarHLayout)

    def chooseImportFileDialog(self) -> bool:
        file, _ = QFileDialog.getOpenFileName(self, "Open file to import from", filter=FILTER_IMPORT_FILES)
        self.setImportFile(file)

    def setImportFile(self, file: str):
        self.importFile = file
        self.fileType = file.rsplit(".")[-1]
        self.importFileLine.setText(f"Import from: {file}")

    def saveMappingFileDialog(self):
        file, _ = QFileDialog.getSaveFileName(self, 'Save Mapping File', filter=JSON_FILES_FILTER)
        if file:
            self.saveMappingFile(file)

    def saveMappingFile(self, file):
        self.mainTreeView.saveMapping(file=file)

    def useMappingFileDialog(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Open and use Mapping File', filter=JSON_FILES_FILTER)
        if file:
            self.useMappingFile(file)

    def useMappingFile(self, file):
        self.mainTreeView.setMapping(file=file)
