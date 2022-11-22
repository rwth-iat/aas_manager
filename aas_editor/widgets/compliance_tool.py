#  Copyright (C) 2022  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QFileDialog, QMessageBox
from basyx.aas.compliance_tool import compliance_check_xml, compliance_check_json, compliance_check_aasx
from basyx.aas.compliance_tool.state_manager import ComplianceToolStateManager

from aas_editor.settings import FILTER_AAS_FILES
from aas_editor.widgets.combobox import ComboBox
from aas_editor.widgets.lineEdit import DropFilePlainTextEdit
from aas_editor import dialogs


class ComplianceToolDialog(QDialog):
    def __init__(self, parent=None):  # <1>
        super().__init__(parent)
        self._initLayout()
        self.setWindowTitle("Compliance Tool")
        self.setMinimumSize(500, 300)

        self.descrLabel = QLabel(self)
        self.descrLabel.setWordWrap(True)
        self.descrLabel.setText('Compliance tool for creating and checking aasx, json and xml files in compliance with '
                                '"Details of the Asset Administration Shell" specification of Plattform Industrie 4.0.')

        self.plainTextEdit = DropFilePlainTextEdit(self, emptyViewMsg="Drop aas file here")
        self.plainTextEdit.setMinimumSize(300, 300)
        #self.plainTextEdit.setEnabled(False)
        self.plainTextEdit.fileDropped.connect(self.checkFile)

        self.optionsComboBox = ComboBox(self)
        self.optionsComboBox.addItem("Show all Logs", 2)
        self.optionsComboBox.addItem("Show only Errors", 1)
        self.optionsComboBox.addItem("Show no Logs", 0)

        self.chooseButton = QPushButton(f"Choose file", self,
                                        toolTip="Choose file",
                                        clicked=self.chooseAndCheckFile)
        self.layout().addWidget(self.plainTextEdit)
        self.layout().addWidget(self.optionsComboBox)
        self.layout().addWidget(self.chooseButton)
        self.layout().addWidget(self.descrLabel)

    def _initLayout(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self)
        self.setLayout(layout)

    def chooseAndCheckFile(self):
        file, _ = QFileDialog.getOpenFileName(self, "Open AAS file",
                                           filter=FILTER_AAS_FILES)
        if file:
            self.checkFile(file)
        else:
            return

    def checkFile(self, file):
        try:
            if file.endswith(".xml"):
                check_schema = compliance_check_xml.check_schema
            elif file.endswith(".json"):
                check_schema = compliance_check_json.check_schema
            elif file.endswith(".aasx"):
                check_schema = compliance_check_aasx.check_schema
            else:
                raise TypeError("File of unknown type:", file)
            manager = ComplianceToolStateManager()
            check_schema(file, manager)
            info = manager.format_state_manager(self.optionsComboBox.currentData())
            self.plainTextEdit.setPlainText(info)
        except Exception as e:
            dialogs.ErrorMessageBox.withTraceback(self, str(e)).exec()
