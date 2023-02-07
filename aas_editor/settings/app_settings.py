#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
import typing
from dataclasses import dataclass

from PyQt5.QtCore import QSize, QSettings
from PyQt5.QtGui import QFont
from PyQt5 import QtCore

from aas_editor.settings.util_constants import NOT_GIVEN

AAS_CREATOR = "PyI40AAS Testing Framework"
APPLICATION_NAME = "AAS Manager"
APPLICATION_INFO = "Free, open source, cross-platform viewer/editor based on PyQt Framework and Eclipse BaSyx Python SDK.\n" \
                   "Developed at the Chair of Information and Automation Systems for Process and Material Technology at RWTH Aachen."
COPYRIGHT_YEAR = 2022
CONTRIBUTORS = "Igor Garmaev"
DEVELOPER_WEB = "plt.rwth-aachen.de"
CONTACT = "i.garmaev@plt.rwth-aachen.de"
REPORT_ERROR_LINK = "https://github.com/zrgt/aas_manager/issues"
APPLICATION_LINK = "https://github.com/zrgt/aas_manager"
ACPLT = "ACPLT"
VERSION = "0.3.2"
LICENSE = "GNU General Public License v3.0"

TOOLBARS_HEIGHT = 30
ATTR_COLUMN_WIDTH = 200

DEFAULT_MAINWINDOW_SIZE = QSize(1194, 624)
MAX_FONT_SIZE = 60
MIN_FONT_SIZE = 6
DEFAULT_FONT = QFont()
DEFAULT_FONT.setWeight(40)
DEFAULT_FONT.setPointSize(12)

MAX_UNDOS = 10
MAX_RECENT_FILES = 10
MAX_SIGNS_TO_SHOW = 1000
MAX_SIGNS_TO_SHOW_IN_TREE = 150

# Custom roles
PACKAGE_ROLE = 1010
NAME_ROLE = 1020
COLUMN_NAME_ROLE = 1025
OBJECT_ROLE = 1030
PARENT_OBJ_ROLE = 1040
PACK_ITEM_ROLE = 1050
LINKED_ITEM_ROLE = 1060
IS_LINK_ROLE = 1070
IS_MEDIA_ROLE = 1080
IS_URL_MEDIA_ROLE = 1090
MEDIA_CONTENT_ROLE = 1100
OPENED_PACKS_ROLE = 1110
OPENED_FILES_ROLE = 1120
ADD_ITEM_ROLE = 1130
CLEAR_ROW_ROLE = 1140
UPDATE_ROLE = 1150
COPY_ROLE = 1155
UNDO_ROLE = 1160
REDO_ROLE = 1170
DATA_CHANGE_FAILED_ROLE = 1180
TYPE_ROLE = 1190
TYPE_HINT_ROLE = 1200
TYPE_CHECK_ROLE = 1210

# Columns
OBJECT_COLUMN_NAME = "object"
OBJECT_VALUE_COLUMN_NAME = "object value"
TYPE_COLUMN_NAME = "type"
TYPEHINT_COLUMN_NAME = "typehint"

DEFAULT_COLUMNS_IN_DETAILED_INFO = (OBJECT_COLUMN_NAME, OBJECT_VALUE_COLUMN_NAME, TYPE_COLUMN_NAME, TYPEHINT_COLUMN_NAME)
DEFAULT_COLUMNS_IN_PACKS_TABLE = (OBJECT_COLUMN_NAME, OBJECT_VALUE_COLUMN_NAME, TYPE_COLUMN_NAME, TYPEHINT_COLUMN_NAME, "_mapping_data")
ATTRIBUTE_COLUMN = 0
VALUE_COLUMN = 1
TYPE_COLUMN = 2
TYPE_HINT_COLUMN = 3

# Themes
import os

files = os.listdir("themes")
THEMES = {"default": "default.qss"}
DEFAULT_THEME = "default"
for file in files:
    if file.endswith(".qss"):
        themename = file.rstrip(".qss")
        THEMES[themename] = f"themes/{file}"

SETTINGS = QSettings("settings.ini", QSettings.IniFormat)


@dataclass(order=True)
class Setting:
    name: str
    default: typing.Any = NOT_GIVEN
    type: typing.Type = NOT_GIVEN

    def setValue(self, value):
        return SETTINGS.setValue(self.name, value)

    def value(self):
        args = [self.name]
        if self.default != NOT_GIVEN:
            args.append(self.default)
        if self.type != NOT_GIVEN:
            args.append(self.type)
        return SETTINGS.value(*args)


class AppSettings:
    THEME = Setting('theme', DEFAULT_THEME, str)
    SIZE = Setting('size', DEFAULT_MAINWINDOW_SIZE)
    ORIENTATION = Setting('orientation', QtCore.Qt.Vertical, int)
    LEFT_ZONE_SIZE = Setting('leftZoneSize', QSize(300, 624))
    RIGHT_ZONE_SIZE = Setting('rightZoneSize', QSize(300, 624))
    OPENED_AAS_FILES = Setting('openedAasFiles', set())
    FONTSIZE_FILES_VIEW = Setting('fontSizeFilesView', DEFAULT_FONT.pointSize(), int)
    FONTSIZE_DETAILED_VIEW = Setting('fontSizeDetailedView', DEFAULT_FONT.pointSize(), int)
    PACKTREEVIEW_HEADER_STATE = Setting('packTreeViewHeaderState', None)
    PACKTREEVIEW_HEADER_CUSTOM_COLUMN_LISTS_FILE = "custom_column_lists.json"
    TABTREEVIEW_HEADER_STATE = Setting('tabTreeViewHeaderState', None)
    DEFAULT_NEW_FILETYPE_FILTER = Setting('defaultNewFileTypeFilter', "AASX files (*.aasx)", str)

    # If True, JSON parts are created for the AAS and each submodel
    # in the AASX file instead of XML parts.
    WRITE_JSON_IN_AASX = Setting('writeJsonInAasx', False, bool)
    # If True, submodels are written to separate AASX parts
    # instead of being included in the AAS part with in the AASX package.
    ALL_SUBMODEL_REFS_TO_AAS = Setting('allSubmodelRefsToAas', True, bool)
    WRITE_PRETTY_JSON = Setting('writePrettyJson', False, bool)
