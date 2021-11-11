#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
import qtawesome as qta
from PyQt5.QtGui import QColor, QIcon

from aas_editor.settings.colors import LIGHT_BLUE

ICON_DEFAULTS = {'scale_factor': 1.0,
                 'color': QColor(LIGHT_BLUE.red(), LIGHT_BLUE.green(), LIGHT_BLUE.blue(), 225),
                 'color_active': QColor(LIGHT_BLUE.red(), LIGHT_BLUE.green(), LIGHT_BLUE.blue(),
                                        255),
                 'color_disabled': QColor(LIGHT_BLUE.red(), LIGHT_BLUE.green(), LIGHT_BLUE.blue(),
                                          50), }

qta.set_defaults(**ICON_DEFAULTS)

APP_ICON=QIcon('aas_editor/icons/logo.svg')
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

# Distances between chars in icon
CHARS_ICON_LEN_SETTINGS = {
    1: [{'offset': (0, 0)}],
    2: [{'offset': (-0.20, 0)}, {'offset': (0.20, 0)}],
    3: [{'offset': (-0.36, 0)}, {'offset': (0, 0)}, {'offset': (0.36, 0)}],
    4: [{'offset': (-0.40, 0)}, {'offset': (-0.13, 0)}, {'offset': (0.13, 0)}, {'offset': (0.40, 0)}]
    # 4: [{'offset': (-0.48, 0)}, {'offset': (-0.15, 0)}, {'offset': (0.15, 0)}, {'offset': (0.48, 0)}]
}


def getCharsIcon(chars: str):
    if len(chars) > 4:
        raise ValueError("Max 4 characters allowed for an icon", chars)
    else:
        options = CHARS_ICON_LEN_SETTINGS[len(chars)]

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
