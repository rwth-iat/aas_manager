#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QGroupBox, QHBoxLayout, QRadioButton
from PyQt5.QtCore import Qt

from aas_editor.settings import FILE_TYPE_FILTERS, SETTINGS, AppSettings


class OptionGroupBox(QGroupBox):
    def currSetting(self):
        pass

    def newSetting(self):
        pass

    def applyNewSetting(self):
        pass


class DefaultNewFiletype(OptionGroupBox):
    """Groupbox to choose default type of new file"""
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.setTitle("Standard initialisation file type")
        self.setAlignment(Qt.AlignLeft)
        layout = QHBoxLayout(self)
        self.setLayout(layout)

        self.radiobtns = []
        for typ in list(FILE_TYPE_FILTERS.keys()):
            btn = QRadioButton(typ)
            self.radiobtns.append(btn)
            layout.addWidget(btn)
            if self.currSetting() == FILE_TYPE_FILTERS[typ]:
                btn.setChecked(True)

    def find_checked_radiobutton(self):
        for btn in self.radiobtns:
            if btn.isChecked():
                return btn

    def currSetting(self):
        return SETTINGS.value(AppSettings.DEFAULT_NEW_FILETYPE_FILTER.name,
                              AppSettings.DEFAULT_NEW_FILETYPE_FILTER.default)

    def newSetting(self):
        typ = self.find_checked_radiobutton().text()
        typ_filter = FILE_TYPE_FILTERS[typ]
        return typ_filter

    def applyNewSetting(self):
        SETTINGS.setValue(AppSettings.DEFAULT_NEW_FILETYPE_FILTER.name, self.newSetting())


class SettingsDialog(QDialog):
    def __init__(self, parent=None):  # <1>
        super().__init__(parent)

        self.setWindowTitle("Settings")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.optionGroupBoxes = []
        self.optionGroupBoxes.append(DefaultNewFiletype(self))

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
            optionGroupBox.applyNewSetting()
