#  Copyright (C) 2025  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
import traceback
import webbrowser

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QMessageBox

from settings import APPLICATION_NAME, APPLICATION_INFO, DEVELOPER_WEB, APPLICATION_LINK, VERSION, \
    AAS_METAMODEL_VERSION, CONTRIBUTORS, CONTACT, LICENSE, COPYRIGHT_YEAR, REPORT_ERROR_LINK


class AboutMessageBox(QMessageBox):
    def __init__(self, parent=None):  # <1>
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setTextFormat(Qt.TextFormat.RichText)
        self.setText(
            f"{APPLICATION_NAME}<br>"
            f"{APPLICATION_INFO}<br><br>"
            f"Website: <a href='{DEVELOPER_WEB}'>{DEVELOPER_WEB}</a><br>"
            f"Project Homepage: <a href='{APPLICATION_LINK}'>{APPLICATION_LINK}</a><br>"
            f"Version: {VERSION}<br>"
            f"AAS Metamodel Version: {AAS_METAMODEL_VERSION}<br>"
            f"Contributors: {CONTRIBUTORS}<br>"
            f"Contact: {CONTACT}<br>"
            f"License: {LICENSE}<br>"
            f"Copyright (C) {COPYRIGHT_YEAR}"
        )
        self.setIconPixmap(self.parentWidget().windowIcon().pixmap(QSize(64, 64)))


class ErrorMessageBox(QMessageBox):
    def __init__(self, parent):
        super().__init__(parent)
        self.setMinimumWidth(400)
        self.setIcon(QMessageBox.Icon.Critical)
        self.setWindowTitle("Error")

        # Each Error message box will have "Report Button" for opening an url
        self.setStandardButtons(QMessageBox.StandardButton.Ok)
        reportButton = self.addButton("Report Bug", QMessageBox.ButtonRole.HelpRole)
        reportButton.clicked.disconnect()
        reportButton.clicked.connect(self.reportButtonClicked)

    def reportButtonClicked(self):
        webbrowser.open(REPORT_ERROR_LINK)

    @classmethod
    def withTraceback(cls, parent, text: str):
        err_msg = traceback.format_exc()
        box = cls(parent)
        box.setText(text)
        box.setDetailedText(err_msg)
        return box

    @classmethod
    def withDetailedText(cls, parent, text: str):
        box = cls(parent)
        if "\n\n" in text:
            text, detailedText = text.split("\n\n", 1)
            box.setDetailedText(detailedText)
        box.setText(text)
        return box
