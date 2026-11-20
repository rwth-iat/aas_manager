#  Copyright (C) 2026  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QColor, QPainter, QPixmap
from PyQt6.QtWidgets import QSplashScreen

from aas_editor.settings.app_settings import (COPYRIGHT_YEAR, ICONS_FOLDER, LICENSE,
                                              PYPROJECT_TOML, VERSION)

WIDTH, HEIGHT = 600, 340
SCALE = 2  # draw at double resolution, sharp on HiDPI screens


def newSplash() -> QSplashScreen:
    """Startup screen: app logo, IAT-RWTH logo, author and copyright."""
    pixmap = QPixmap(WIDTH * SCALE, HEIGHT * SCALE)
    pixmap.setDevicePixelRatio(SCALE)
    pixmap.fill(QColor("white"))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    _drawCentered(painter, QPixmap(str(ICONS_FOLDER / "full_logo.png")), 30, 380)
    _drawCentered(painter, QPixmap(str(ICONS_FOLDER / "iat_rwth_logo.png")), 190, 420)
    painter.end()

    author = PYPROJECT_TOML["project"]["authors"][0]["name"]
    splash = QSplashScreen(pixmap)
    splash.showMessage(
        f"Version {VERSION} · © 2021–{COPYRIGHT_YEAR} {author}, "
        f"IAT, RWTH Aachen University\n{LICENSE}",
        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
        QColor("#555555"),
    )
    return splash


def _drawCentered(painter: QPainter, image: QPixmap, top: int, width: int) -> None:
    height = round(image.height() * width / image.width())
    painter.drawPixmap(QRect((WIDTH - width) // 2, top, width, height), image)
