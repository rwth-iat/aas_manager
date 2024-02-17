#  Copyright (C) 2022  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
from PyQt6.QtWidgets import QWidget, QHBoxLayout

from aas_editor.additional.classes import DictItem
from aas_editor.widgets.lineEdit import LineEdit


class DictItemEdit(QWidget):
    def __init__(self, parent=None):
        super(DictItemEdit, self).__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.keyWidget = LineEdit()
        self.valueWidget = LineEdit()
        self.layout.addWidget(self.keyWidget)
        self.layout.addWidget(self.valueWidget)
        self.setLayout(self.layout)

    def setKeyText(self, text: str):
        self.keyWidget.setText(text)

    def setValueText(self, text: str):
        self.valueWidget.setText(text)

    def setCurrentData(self, data: DictItem):
        self.setKeyText(data.key)
        self.setValueText(data.value)

    def currentData(self) -> DictItem:
        keyData = self.keyWidget.text()
        valueData = self.valueWidget.text()
        return DictItem(keyData, valueData)
