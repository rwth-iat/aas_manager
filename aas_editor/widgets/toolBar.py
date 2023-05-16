#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/

from typing import Optional

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QToolBar, QWidget

from aas_editor.settings.app_settings import TOOLBARS_HEIGHT


class ToolBar(QToolBar):
    def __init__(self, parent: Optional[QWidget] = ...):
        super(ToolBar, self).__init__(parent)
        self.setFixedHeight(TOOLBARS_HEIGHT)
        self.setIconSize(QSize(TOOLBARS_HEIGHT, TOOLBARS_HEIGHT))

    def toggleViewAction(self):
        action = super().toggleViewAction()
        action.setText("Toolbar")
        action.setStatusTip("Show/hide toolbar")
        return action
