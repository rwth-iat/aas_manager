#  Copyright (C) 2022  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
import aas_test_engines.file as test_engines_file_check
from PyQt6.QtWidgets import QDialog, QPushButton, QVBoxLayout, QFileDialog
from aas_editor.settings import FILTER_AAS_FILES
from aas_editor import dialogs
from aas_editor.widgets.dropfilebox import DropFileQWebEngineView


class AasTestEnginesToolDialog(QDialog):
    def __init__(self, parent=None):  # <1>
        super().__init__(parent)
        self._initLayout()
        self.setWindowTitle("AAS-Test-Engines Tool")
        self.setMinimumSize(500, 300)

        description = 'Official test tooling for the Asset Administration Shell: https://github.com/admin-shell-io/aas-test-engines'
        self.html_renderer = DropFileQWebEngineView(self, emptyViewMsg="Drop AAS file to test here", description=description)
        self.html_renderer.setMinimumSize(300, 300)
        self.html_renderer.fileDropped.connect(self.checkFile)

        self.chooseButton = QPushButton(f"Choose file", self,
                                        toolTip="Choose file",
                                        clicked=self.chooseAndCheckFile)
        self.layout().addWidget(self.html_renderer)
        self.layout().addWidget(self.chooseButton)

    def _initLayout(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self)
        self.setLayout(layout)

    def chooseAndCheckFile(self):
        file, _ = QFileDialog.getOpenFileName(self, "Open AAS file", filter=FILTER_AAS_FILES)
        if file:
            self.checkFile(file)
        else:
            return

    def checkFile(self, file):
        try:
            with open(file, "r") as f:
                if file.endswith(".xml"):
                    result = test_engines_file_check.check_xml_file(f)
                elif file.endswith(".json"):
                    result = test_engines_file_check.check_json_file(f)
                elif file.endswith(".aasx"):
                    result = test_engines_file_check.check_aasx_file(f)
                else:
                    raise TypeError("File of unknown type:", file)
            self.html_renderer.setHtml(result.to_html())
        except Exception as e:
            dialogs.ErrorMessageBox.withTraceback(self, str(e)).exec()
