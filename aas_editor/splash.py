#  Copyright (C) 2022  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMessageBox

from aas_editor.settings.app_settings import APPLICATION_NAME, APPLICATION_INFO, DEVELOPER_WEB, APPLICATION_LINK, \
    VERSION, CONTRIBUTORS, CONTACT, LICENSE, COPYRIGHT_YEAR


class Splash(QMessageBox):
    def __init__(self, parent=None):  # <1>
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setTextFormat(Qt.RichText)
        appInfo = APPLICATION_INFO.replace('\n', '<br>')
        self.setText(
            f"{APPLICATION_NAME}<br>"
            f"{appInfo}<br>"
            f" <br>"
            f"Website: <a href='{DEVELOPER_WEB}'>{DEVELOPER_WEB}</a><br>"
            f"Project Homepage: <a href='{APPLICATION_LINK}'>{APPLICATION_LINK}</a><br>"
            f"Version: {VERSION}<br>"
            f"Contributors: {CONTRIBUTORS}<br>"
            f"Contact: {CONTACT}<br>"
            f"License: {LICENSE}<br>"
            f"Copyright (C) {COPYRIGHT_YEAR}"
        )
        self.setIconPixmap(QPixmap("aas_editor/icons/logo.svg"))
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setObjectName("splashWindow")
        self.setStyleSheet("#splashWindow{border:0.2ex solid rgba(186, 185, 184, 0.5);}")
