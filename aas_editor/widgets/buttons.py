#  Copyright (C) 2025  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/

from PyQt6.QtWidgets import QPushButton, QToolButton


class CreateOptionalParamBtn(QPushButton):
    def __init__(self, title, paramName, objTypehint, **kwargs):
        super(CreateOptionalParamBtn, self).__init__(title, **kwargs)
        self.paramName = paramName
        self.paramTypehint = objTypehint


class CloseButton(QToolButton):
    """Close button for optional params.
    A separate class is needed for the stylesheet to work properly"""
    def __init__(self, parent=None):
        super(CloseButton, self).__init__(parent)
