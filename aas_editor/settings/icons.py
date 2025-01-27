#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
from PyQt6.QtCore import Qt
from directories import get_icons_folder

from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap, QFont
from PyQt6.QtSvg import QSvgRenderer

from aas_editor.settings.colors import LIGHT_BLUE


ICON_COLOR = QColor(LIGHT_BLUE.red(), LIGHT_BLUE.green(), LIGHT_BLUE.blue(), 225)
ICON_COLOR_ACTIVE = QColor(LIGHT_BLUE.red(), LIGHT_BLUE.green(), LIGHT_BLUE.blue(), 255)
ICON_COLOR_DISABLED = QColor(LIGHT_BLUE.red(), LIGHT_BLUE.green(), LIGHT_BLUE.blue(), 50)

def create_colored_svg_icon(file_path,
                            color_normal=ICON_COLOR,
                            color_active=ICON_COLOR_ACTIVE,
                            color_disabled=ICON_COLOR_DISABLED):
    """
    Create a QIcon from an SVG file with customizable colors for normal, active, and disabled states.

    Args:
        file_path (str): Path to the SVG file.
        color_normal (QColor): Color for the normal state.
        color_active (QColor): Color for the active state.
        color_disabled (QColor): Color for the disabled state.

    Returns:
        QIcon: An icon with different colors for each state.
    """
    def render_svg_with_color(file_path, color):
        """Render an SVG file with a specific color."""
        renderer = QSvgRenderer(file_path)
        pixmap = QPixmap(renderer.defaultSize())
        pixmap.fill(QColor("transparent"))  # Transparent background
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)  # Apply color
        painter.fillRect(pixmap.rect(), color)
        painter.end()
        return pixmap

    # Create pixmaps for each state
    pixmap_normal = render_svg_with_color(file_path, color_normal)
    pixmap_active = render_svg_with_color(file_path, color_active)
    pixmap_disabled = render_svg_with_color(file_path, color_disabled)

    # Create a QIcon and add the pixmaps for each state
    icon = QIcon()
    icon.addPixmap(pixmap_normal, QIcon.Mode.Normal)  # Normal state
    icon.addPixmap(pixmap_active, QIcon.Mode.Active)  # Active state
    icon.addPixmap(pixmap_disabled, QIcon.Mode.Disabled)  # Disabled state

    return icon


ICONS_FOLDER = get_icons_folder()


# Define icons using SVG/PNG files
EXIT_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/exit-to-app.svg")
NEW_PACK_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/folder-plus.svg")
OPEN_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/folder-open.svg")
OPEN_DRAG_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/open-in-app.svg")
SAVE_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/content-save.svg")
SAVE_ALL_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/content-save-all.svg")
SETTINGS_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/cog.svg")
COPY_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/content-copy.svg")
PASTE_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/content-paste.svg")
CUT_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/content-cut.svg")
ADD_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/plus-circle.svg")
DEL_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/delete.svg")
UPDATE_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/update.svg")
EDIT_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/playlist-edit.svg")
UNDO_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/undo.svg")
REDO_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/redo.svg")
FORWARD_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/arrow-right-circle.svg")
BACK_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/arrow-left-circle.svg")
SPLIT_VERT_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/arrow-split-vertical.svg")
SPLIT_HORIZ_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/arrow-split-horizontal.svg")
ZOOM_IN_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/magnify-plus.svg")
ZOOM_OUT_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/magnify-minus.svg")
NEXT_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/arrow-down.svg")
PREV_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/arrow-up.svg")
FILTER_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/filter.svg")
REGEX_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/regex.svg")
CASE_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/format-letter-case.svg")
CLOSE_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/close.svg")
EXPAND_ALL_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/arrow-expand-vertical.svg")
COLLAPSE_ALL_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/arrow-collapse-vertical.svg")
AUTOSCROLL_TO_SRC_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/package-down.svg")
AUTOSCROLL_FROM_SRC_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/package-up.svg")
FILE_ICON = create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/file.svg")

MIME_TYPE_ICON_DICT = {
    "application/pdf": create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/file-pdf-box.svg"),
    "image": create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/file-image.svg"),
    "text": create_colored_svg_icon(str(ICONS_FOLDER.absolute().as_posix()) + "/file-document.svg"),
}

# Distances between chars in icon
CHARS_ICON_LEN_SETTINGS = {
    1: [{'offset': (0, 0)}],
    2: [{'offset': (-0.20, 0)}, {'offset': (0.20, 0)}],
    3: [{'offset': (-0.36, 0)}, {'offset': (0, 0)}, {'offset': (0.36, 0)}],
    4: [{'offset': (-0.40, 0)}, {'offset': (-0.13, 0)}, {'offset': (0.13, 0)}, {'offset': (0.40, 0)}]
    # 4: [{'offset': (-0.48, 0)}, {'offset': (-0.15, 0)}, {'offset': (0.15, 0)}, {'offset': (0.48, 0)}]
}


def getCharsIcon(chars: str, font_size: int = 24, color: QColor = LIGHT_BLUE, background_color: QColor = QColor("transparent")):
    """
    Generate a QIcon from a string of characters.

    Args:
        chars (str): The characters to render as an icon (max 4 characters).
        font_size (int): The font size for the characters.
        color (QColor): The color of the characters.
        background_color (QColor): The background color of the icon.

    Returns:
        QIcon: An icon created from the characters.
    """
    if len(chars) > 4:
        raise ValueError("Max 4 characters allowed for an icon")

    # Create a pixmap to render the characters
    size = font_size * 2  # Adjust size based on font size
    pixmap = QPixmap(size, size)
    pixmap.fill(background_color)  # Set background color

    # Set up the painter
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    # Set font
    font = QFont("Monospace")
    font.setPointSize(font_size)
    font.setBold(True)
    painter.setFont(font)

    # Set pen color
    painter.setPen(color)

    # Draw each character individually with tight spacing
    char_width = font_size * 0.6  # Adjusted for a compact font
    x_offset = 0  # Start drawing from the left padding
    y_offset = (size - font_size) / 2  # Center vertically
    char_spacing: int = 2
    for char in chars:
        # Draw the character at the current position
        painter.drawText(int(x_offset), int(y_offset + font_size), char)
        # Move the x_offset for the next character
        x_offset += char_width + char_spacing
    painter.end()

    # Convert the pixmap to a QIcon
    return QIcon(pixmap)
