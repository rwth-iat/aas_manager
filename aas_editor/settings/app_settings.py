import qtawesome
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QKeySequence, QColor, QFont

AAS_CREATOR = "PyI40AAS Testing Framework"
APPLICATION_NAME = "AAS Editor"
ACPLT = "ACPLT"

NOT_GIVEN = "NotGivenValueAASEditor"

TOOLBARS_HEIGHT = 30
ATTR_COLUMN_WIDTH = 200

DEFAULT_MAINWINDOW_SIZE = QSize(1194, 624)
MAX_FONT_SIZE = 60
MIN_FONT_SIZE = 6
DEFAULT_FONT = QFont()
DEFAULT_FONT.setPointSize(12)

MAX_UNDOS = 10
MAX_RECENT_FILES = 4

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
COLUMNS_IN_DETAILED_INFO = ("attribute", "value", "type", "typehint")
COLUMNS_IN_PACKS_TABLE = ("attribute", "value", "type", "typehint")
ATTRIBUTE_COLUMN = 0
VALUE_COLUMN = 1
TYPE_COLUMN = 2
TYPE_HINT_COLUMN = 3

# Themes
DEFAULT_THEME = "dark"
DARK_THEME_PATH = "themes/dark.qss"
LIGHT_THEME_PATH = "themes/light.qss"
THEMES = {"dark": DARK_THEME_PATH, "light": LIGHT_THEME_PATH, "standard": ""}

# Colors
LIGHT_BLUE = QColor(132, 185, 255)
LINK_BLUE = QColor(26, 13, 171)
CHANGED_BLUE = QColor(83, 148, 236, 255)
HIGHLIGHT_YELLOW = QColor(255, 255, 0, 130)
RED = QColor("red")
NEW_GREEN = QColor("green")

# ICONS
import qtawesome as qta

ICON_DEFAULTS = {'scale_factor': 1.2,
                 'color': QColor(LIGHT_BLUE.red(), LIGHT_BLUE.green(), LIGHT_BLUE.blue(), 225),
                 'color_active': QColor(LIGHT_BLUE.red(), LIGHT_BLUE.green(), LIGHT_BLUE.blue(),
                                        255),
                 'color_disabled': QColor(LIGHT_BLUE.red(), LIGHT_BLUE.green(), LIGHT_BLUE.blue(),
                                          50), }
qta.set_defaults(**ICON_DEFAULTS)

EXIT_ICON = qta.icon("mdi.exit-to-app")
NEW_PACK_ICON = qta.icon("mdi.folder-plus")
OPEN_ICON = qta.icon("mdi.folder-open")
OPEN_DRAG_ICON = qta.icon("mdi.open-in-app")
SAVE_ICON = qta.icon("mdi.content-save")
SAVE_ALL_ICON = qta.icon("mdi.content-save-all")
SETTINGS_ICON = qta.icon("mdi.cog")
VIEW_ICON = qta.icon("mdi.view-list")

COPY_ICON = qta.icon("mdi.content-copy")
PASTE_ICON = qta.icon("mdi.content-paste")
CUT_ICON = qta.icon("mdi.content-cut")
ADD_ICON = qta.icon("mdi.plus-circle")
DEL_ICON = qta.icon("mdi.delete")
EDIT_ICON = qta.icon("mdi.playlist-edit")
UNDO_ICON = qta.icon("mdi.undo")
REDO_ICON = qta.icon("mdi.redo")

FORWARD_ICON = qta.icon("fa5s.arrow-circle-right")
BACK_ICON = qta.icon("fa5s.arrow-circle-left")

SPLIT_VERT_ICON = qta.icon("mdi.arrow-split-vertical")
SPLIT_HORIZ_ICON = qta.icon("mdi.arrow-split-horizontal")

ZOOM_IN_ICON = qta.icon("mdi.magnify-plus")
ZOOM_OUT_ICON = qta.icon("mdi.magnify-minus")

NEXT_ICON = qta.icon("mdi.arrow-down")
PREV_ICON = qta.icon("mdi.arrow-up")
FILTER_ICON = qta.icon("mdi.filter")
REGEX_ICON = qta.icon("mdi.regex")
CASE_ICON = qta.icon("mdi.format-letter-case")
CLOSE_ICON = qta.icon("mdi.close")

EXPAND_ALL_ICON = qta.icon("mdi.arrow-expand-vertical")
COLLAPSE_ALL_ICON = qta.icon("mdi.arrow-collapse-vertical")
AUTOSCROLL_TO_SRC_ICON = qta.icon("mdi.package-down")
AUTOSCROLL_FROM_SRC_ICON = qta.icon("mdi.package-up")

FILE_ICON = qta.icon("mdi.file")
MIME_TYPE_ICON_DICT = {
    "application/pdf": qta.icon("mdi.file-pdf"),
    "image": qta.icon("mdi.file-image"),
    "text": qta.icon("mdi.file-document"),
}

# CHARS4=[{'offset': (-0.48, 0)}, {'offset': (-0.16, 0)},
#         {'offset': (0.15, 0)}, {'offset': (0.46, 0)}]
CHARS1_3 = [{'offset': (-0.48, 0)}, {'offset': (-0.13, 0)},
            {'offset': (0.18, 0)}, {'offset': (0.48, 0)}]
# CHARS3=[{'offset': (-0.3, 0)}, {'offset': (0, 0)}, {'offset': (0.3, 0)}]
CHARS3 = [{'offset': (-0.36, 0)}, {'offset': (0, 0)}, {'offset': (0.36, 0)}]
CHARS4 = [{'offset': (-0.48, 0)}, {'offset': (-0.15, 0)},
        {'offset': (0.15, 0)}, {'offset': (0.48, 0)}]
CHARS1_3=CHARS4


def getCharsIcon(chars: str):
    if len(chars) == 3:
        options = CHARS3
    elif len(chars) == 4:
        options = CHARS4

    mdiChar = "mdi.alpha"
    args = []
    for char in chars.lower():
        args.append(f"{mdiChar}-{char}")
    return qta.icon(*args, options=options)

# element icons
ELEM_ICON_DEFAULTS = {'scale_factor': 1.6,
                      'color': QColor(LIGHT_BLUE.red(), LIGHT_BLUE.green(), LIGHT_BLUE.blue(), 255),
                      }
qta.set_defaults(**ELEM_ICON_DEFAULTS)

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
