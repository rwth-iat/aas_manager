#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap, QFont
from PyQt6.QtSvg import QSvgRenderer

from aas_editor.settings.colors import LIGHT_BLUE

ICON_COLOR = QColor(LIGHT_BLUE.red(), LIGHT_BLUE.green(), LIGHT_BLUE.blue(), 225)
ICON_COLOR_ACTIVE = QColor(LIGHT_BLUE.red(), LIGHT_BLUE.green(), LIGHT_BLUE.blue(), 255)
ICON_COLOR_DISABLED = QColor(LIGHT_BLUE.red(), LIGHT_BLUE.green(), LIGHT_BLUE.blue(), 50)


def getCharsIcon(chars: str, font_size: int = 24, color: QColor = LIGHT_BLUE,
                 background_color: QColor = QColor("transparent")):
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


def transform_svg_to_icon(target_icon: QIcon, file_path,
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
    target_icon.addPixmap(pixmap_normal, QIcon.Mode.Normal)  # Normal state
    target_icon.addPixmap(pixmap_active, QIcon.Mode.Active)  # Active state
    target_icon.addPixmap(pixmap_disabled, QIcon.Mode.Disabled)  # Disabled state

    return target_icon

EXIT_ICON = QIcon()
NEW_PACK_ICON = QIcon()
OPEN_ICON = QIcon()
OPEN_DRAG_ICON = QIcon()
SAVE_ICON = QIcon()
SAVE_ALL_ICON = QIcon()
SETTINGS_ICON = QIcon()
COPY_ICON = QIcon()
PASTE_ICON = QIcon()
CUT_ICON = QIcon()
ADD_ICON = QIcon()
DEL_ICON = QIcon()
UPDATE_ICON = QIcon()
EDIT_ICON = QIcon()
EDIT_JSON_ICON = QIcon()
UNDO_ICON = QIcon()
REDO_ICON = QIcon()
FORWARD_ICON = QIcon()
BACK_ICON = QIcon()
SPLIT_VERT_ICON = QIcon()
SPLIT_HORIZ_ICON = QIcon()
ZOOM_IN_ICON = QIcon()
ZOOM_OUT_ICON = QIcon()
NEXT_ICON = QIcon()
PREV_ICON = QIcon()
FILTER_ICON = QIcon()
REGEX_ICON = QIcon()
CASE_ICON = QIcon()
CLOSE_ICON = QIcon()
EXPAND_ALL_ICON = QIcon()
COLLAPSE_ALL_ICON = QIcon()
AUTOSCROLL_TO_SRC_ICON = QIcon()
AUTOSCROLL_FROM_SRC_ICON = QIcon()
FILE_ICON = QIcon()
MIME_PDF_ICON = QIcon()
MIME_IMAGE_ICON = QIcon()
MIME_TEXT_ICON = QIcon()

MIME_TYPE_ICON_DICT = {
    "application/pdf": MIME_PDF_ICON,
    "image": MIME_IMAGE_ICON,
    "text": MIME_TEXT_ICON,
}

ICONS_SVG = {
    EXIT_ICON: "exit-to-app.svg",
    NEW_PACK_ICON: "folder-plus.svg",
    OPEN_ICON: "folder-open.svg",
    OPEN_DRAG_ICON: "open-in-app.svg",
    SAVE_ICON: "content-save.svg",
    SAVE_ALL_ICON: "content-save-all.svg",
    SETTINGS_ICON: "cog.svg",
    COPY_ICON: "content-copy.svg",
    PASTE_ICON: "content-paste.svg",
    CUT_ICON: "content-cut.svg",
    ADD_ICON: "plus-circle.svg",
    DEL_ICON: "delete.svg",
    UPDATE_ICON: "update.svg",
    EDIT_ICON: "table-edit.svg",
    EDIT_JSON_ICON: "playlist-edit.svg",
    UNDO_ICON: "undo.svg",
    REDO_ICON: "redo.svg",
    FORWARD_ICON: "arrow-right-circle.svg",
    BACK_ICON: "arrow-left-circle.svg",
    SPLIT_VERT_ICON: "arrow-split-vertical.svg",
    SPLIT_HORIZ_ICON: "arrow-split-horizontal.svg",
    ZOOM_IN_ICON: "magnify-plus.svg",
    ZOOM_OUT_ICON: "magnify-minus.svg",
    NEXT_ICON: "arrow-down.svg",
    PREV_ICON: "arrow-up.svg",
    FILTER_ICON: "filter.svg",
    REGEX_ICON: "regex.svg",
    CASE_ICON: "format-letter-case.svg",
    CLOSE_ICON: "close.svg",
    EXPAND_ALL_ICON: "arrow-expand-vertical.svg",
    COLLAPSE_ALL_ICON: "arrow-collapse-vertical.svg",
    AUTOSCROLL_TO_SRC_ICON: "package-down.svg",
    AUTOSCROLL_FROM_SRC_ICON: "package-up.svg",
    FILE_ICON: "file.svg",
    MIME_PDF_ICON: "file-pdf-box.svg",
    MIME_IMAGE_ICON: "file-image.svg",
    MIME_TEXT_ICON: "file-document.svg",
}

def initialize_all_icons():
    from aas_editor.settings.app_settings import ICONS_FOLDER
    for icon, svg_file in ICONS_SVG.items():
        transform_svg_to_icon(icon, str(ICONS_FOLDER / svg_file))
