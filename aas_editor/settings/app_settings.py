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

from PyQt5.QtCore import Qt, QSize, QSettings
from PyQt5.QtGui import QKeySequence, QFont
from PyQt5.QtWidgets import QFileDialog

from aas_editor.settings.aas_settings import FILE_TYPE_FILTERS

AAS_CREATOR = "PyI40AAS Testing Framework"
APPLICATION_NAME = "AAS Manager"
COPYRIGHT_YEAR = 2021
CONTRIBUTORS = "Igor Garmaev"
CONTACT = "garmaev@gmx.net"
ACPLT = "ACPLT"

NOT_GIVEN = "NotGivenValueAASEditor"

TOOLBARS_HEIGHT = 30
ATTR_COLUMN_WIDTH = 200

DEFAULT_MAINWINDOW_SIZE = QSize(1194, 624)
MAX_FONT_SIZE = 60
MIN_FONT_SIZE = 6
DEFAULT_FONT = QFont()
DEFAULT_FONT.setWeight(40)
DEFAULT_FONT.setPointSize(12)

MAX_UNDOS = 10
MAX_RECENT_FILES = 4

#FileDialogOptions
FILE_DIALOG_OPTIONS = QFileDialog.DontResolveSymlinks | QFileDialog.DontUseNativeDialog

# Custom roles
PACKAGE_ROLE = 1001
NAME_ROLE = 1002
OBJECT_ROLE = 1003
PARENT_OBJ_ROLE = 1004
PACK_ITEM_ROLE = 1005
LINKED_ITEM_ROLE = 1006
IS_LINK_ROLE = 1007
IS_MEDIA_ROLE = 1008
IS_URL_MEDIA_ROLE = 1015
MEDIA_CONTENT_ROLE = 1016
OPENED_PACKS_ROLE = 1009
OPENED_FILES_ROLE = 1010
ADD_ITEM_ROLE = 1011
CLEAR_ROW_ROLE = 1012
UNDO_ROLE = 1019
REDO_ROLE = 1020
DATA_CHANGE_FAILED_ROLE = 1013
TYPE_ROLE = 1018
TYPE_HINT_ROLE = 1014
TYPE_CHECK_ROLE = 1017

# Columns
COLUMNS_IN_DETAILED_INFO = ("attribute", "value", "type")
COLUMNS_IN_PACKS_TABLE = ("attribute", "value", "type")
ATTRIBUTE_COLUMN = 0
VALUE_COLUMN = 1
TYPE_COLUMN = 2
TYPE_HINT_COLUMN = 3

# Themes
import os
files = os.listdir("themes")
THEMES = {"standard": ""}
DEFAULT_THEME = "standard"
for file in files:
    if file.endswith(".qss"):
        themename = file.rstrip(".qss")
        THEMES[themename] = f"themes/{file}"


# Shortcuts
SC_COPY = QKeySequence.Copy
SC_CUT = QKeySequence.Cut
SC_PASTE = QKeySequence.Paste
SC_DELETE = QKeySequence.Delete
SC_NEW = QKeySequence.New
SC_REDO = QKeySequence.Redo
SC_UNDO = QKeySequence.Undo

SC_ZOOM_IN = QKeySequence(Qt.CTRL + Qt.Key_Plus)
SC_ZOOM_OUT = QKeySequence(Qt.CTRL + Qt.Key_Minus)

SC_EXPAND_RECURS = QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_Plus)
SC_EXPAND_ALL = QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Plus)
SC_COLLAPSE_RECURS = QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_Minus)
SC_COLLAPSE_ALL = QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Minus)

SC_OPEN = QKeySequence(Qt.CTRL + Qt.Key_O)
SC_SAVE_ALL = QKeySequence(Qt.CTRL + Qt.Key_S)
SC_BACK = QKeySequence.Back
SC_FORWARD = QKeySequence.Forward

SC_SEARCH = QKeySequence(Qt.CTRL + Qt.Key_F)

SC_FOCUS2RIGTH_TREE = QKeySequence(Qt.CTRL + Qt.RightArrow)
SC_FOCUS2LEFT_TREE = QKeySequence(Qt.CTRL + Qt.LeftArrow)


@dataclass
class Setting:
    name: str
    default: typing.Any


class AppSettings:
    THEME = Setting('theme', DEFAULT_THEME)
    SIZE = Setting('size', DEFAULT_MAINWINDOW_SIZE)
    LEFT_ZONE_SIZE = Setting('leftZoneSize', QSize(300, 624))
    RIGHT_ZONE_SIZE = Setting('rightZoneSize', QSize(300, 624))
    OPENED_AAS_FILES = Setting('openedAasFiles', set())
    FONTSIZE_FILES_VIEW = Setting('fontSizeFilesView', DEFAULT_FONT.pointSize())
    FONTSIZE_DETAILED_VIEW = Setting('fontSizeDetailedView', DEFAULT_FONT.pointSize())
    DEFAULT_NEW_FILETYPE_FILTER = Setting('defaultNewFileTypeFilter', FILE_TYPE_FILTERS["AASX"])
    PACKTREEVIEW_HEADER_STATE = Setting('packTreeViewHeaderState', None)
    TABTREEVIEW_HEADER_STATE = Setting('tabTreeViewHeaderState', None)

SETTINGS = QSettings("settings.ini", QSettings.IniFormat)
