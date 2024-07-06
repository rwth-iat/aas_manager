#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
from typing import Dict

from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QGroupBox, QHBoxLayout, QRadioButton
from PyQt6.QtCore import Qt

from aas_editor.settings import AppSettings, Setting, FILE_TYPES


class OptionGroupBox(QGroupBox):
    def currOption(self):
        pass

    def chosenOption(self):
        pass

    def applyChosenOption(self):
        pass


class RadioBtnsGroupBox(OptionGroupBox):
    """Groupbox to choose default type of new file"""
    def __init__(self, parent, title, options: Dict[str, any], appSetting: Setting, **kwargs):
        super().__init__(parent, **kwargs)
        self.setTitle(title)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout = QHBoxLayout(self)
        self.setLayout(layout)

        self.appSetting = appSetting
        self.options = options

        self.radiobtns = []
        for optionName in self.options:
            btn = QRadioButton(optionName)
            self.radiobtns.append(btn)
            layout.addWidget(btn)
            if self.currOption() == options[optionName]:
                btn.setChecked(True)

    def find_checked_radiobutton(self):
        for btn in self.radiobtns:
            if btn.isChecked():
                return btn

    def currOption(self):
        return self.appSetting.value()

    def chosenOption(self):
        optionName = self.find_checked_radiobutton().text()
        chosenOption = self.options[optionName]
        return chosenOption

    def applyChosenOption(self):
        self.appSetting.setValue(self.chosenOption())


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Settings")

        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.optionGroupBoxes = [
            RadioBtnsGroupBox(self, title="Standard initialisation file type",
                              options=FILE_TYPES,
                              appSetting=AppSettings.DEFAULT_NEW_FILETYPE),
            RadioBtnsGroupBox(self, title="Filetype for saving in AASX",
                              options={"JSON": True, "XML": False},
                              appSetting=AppSettings.WRITE_JSON_IN_AASX),
            RadioBtnsGroupBox(self, title="Save JSON in pretty style",
                              options={"Yes": True, "No": False},
                              appSetting=AppSettings.WRITE_PRETTY_JSON),
            RadioBtnsGroupBox(self, title="Automatically add references of existing submodels to the first AAS when "
                                          "saving file",
                              options={"Yes": True, "No": False},
                              appSetting=AppSettings.ALL_SUBMODEL_REFS_TO_AAS),
            ]

        self.layout = QVBoxLayout()
        message = QLabel("App settings")
        self.layout.addWidget(message)
        for groupbox in self.optionGroupBoxes:
            self.layout.addWidget(groupbox)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def accept(self) -> None:
        self.applySettings()
        super(SettingsDialog, self).accept()

    def applySettings(self) -> None:
        for optionGroupBox in self.optionGroupBoxes:
            optionGroupBox.applyChosenOption()
