#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
import datetime
import typing
from dataclasses import dataclass
from pathlib import Path

import toml
from PyQt6.QtCore import QSize, QSettings
from PyQt6.QtGui import QFont, QIcon
from PyQt6 import QtCore

from aas_editor.directories import get_settings_file, get_themes_folder, get_custom_column_lists_file, get_icons_folder
from aas_editor.settings.util_constants import NOT_GIVEN

PYPROJECT_TOML_FILE = Path(__file__).parent.parent.parent / "pyproject.toml"
PYPROJECT_TOML = toml.load(PYPROJECT_TOML_FILE)

VERSION = PYPROJECT_TOML["project"]["version"]
APPLICATION_NAME = PYPROJECT_TOML["project"]["display_name"]
APPLICATION_INFO = PYPROJECT_TOML["project"]["description"]
COPYRIGHT_YEAR = datetime.datetime.now().year
CONTRIBUTORS = ", ".join([f"{author['name']}: {author['email']}" for author in PYPROJECT_TOML["project"]["authors"]])
DEVELOPER_WEB = "www.iat.rwth-aachen.de"
CONTACT = PYPROJECT_TOML["project"]["authors"][0]["email"]
REPORT_ERROR_LINK = PYPROJECT_TOML["project"]["urls"]["Issues"]
APPLICATION_LINK = PYPROJECT_TOML["project"]["urls"]["Homepage"]
IAT = "IAT"
LICENSE = PYPROJECT_TOML["project"]["license"]["text"]
AAS_METAMODEL_VERSION = "3.0"

WINDOW_TITLE = f"{APPLICATION_NAME} {VERSION} (Metamodel V{AAS_METAMODEL_VERSION})"

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
DEFAULT_COLUMNS_IN_PACKS_TABLE = (OBJECT_COLUMN_NAME, OBJECT_VALUE_COLUMN_NAME, TYPE_COLUMN_NAME, TYPEHINT_COLUMN_NAME)
DEFAULT_COLUMNS_IN_PACKS_TABLE_TO_SHOW = (OBJECT_COLUMN_NAME, TYPE_COLUMN_NAME)
ATTRIBUTE_COLUMN = 0
VALUE_COLUMN = 1
TYPE_COLUMN = 2
TYPE_HINT_COLUMN = 3

# Files
SETTINGS_FILE = get_settings_file()
THEMES_FOLDER = get_themes_folder()
ICONS_FOLDER = get_icons_folder()
CUSTOM_COLUMN_LISTS_FILE = get_custom_column_lists_file()

# Themes
APP_LOGO = QIcon(str(ICONS_FOLDER / 'logo.svg'))
DEFAULT_THEME = "grey"

SETTINGS = QSettings(str(SETTINGS_FILE), QSettings.IniFormat)


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
    ORIENTATION = Setting('orientation', QtCore.Qt.Orientation.Vertical, int)
    LEFT_ZONE_SIZE = Setting('leftZoneSize', QSize(300, 624))
    RIGHT_ZONE_SIZE = Setting('rightZoneSize', QSize(300, 624))
    AAS_FILES_TO_OPEN_ON_START = Setting('openedAasFiles', set())
    FONTSIZE_FILES_VIEW = Setting('fontSizeFilesView', DEFAULT_FONT.pointSize(), int)
    FONTSIZE_DETAILED_VIEW = Setting('fontSizeDetailedView', DEFAULT_FONT.pointSize(), int)
    PACKTREEVIEW_HEADER_STATE = Setting('packTreeViewHeaderState', None)
    PACKTREEVIEW_HEADER_CUSTOM_COLUMN_LISTS_FILE = CUSTOM_COLUMN_LISTS_FILE
    TABTREEVIEW_HEADER_STATE = Setting('tabTreeViewHeaderState', None)
    DEFAULT_NEW_FILETYPE = Setting('defaultNewFileType', "json", str)

    # If True, JSON parts are created for the AAS and each submodel
    # in the AASX file instead of XML parts.
    WRITE_JSON_IN_AASX = Setting('writeJsonInAasx', False, bool)
    # If True, submodels are written to separate AASX parts
    # instead of being included in the AAS part with in the AASX package.
    ALL_SUBMODEL_REFS_TO_AAS = Setting('allSubmodelRefsToAas', True, bool)
    WRITE_PRETTY_JSON = Setting('writePrettyJson', False, bool)
