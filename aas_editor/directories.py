#  Copyright (C) 2023  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
from pathlib import Path

from PyQt6.QtCore import QDir


def get_settings_file():
    return Path(__file__).resolve().with_name("settings") / "settings.ini"


def create_alias_for_themes_folder(path):
    QDir.addSearchPath('themes', str(path.resolve()))


def get_themes_folder():
    themes_folder = Path(__file__).resolve().with_name("themes")
    create_alias_for_themes_folder(themes_folder)
    return themes_folder


def get_icons_folder():
    return Path(__file__).resolve().with_name("icons")


def get_custom_column_lists_file():
    return Path(__file__).resolve().with_name("custom_column_lists.json")
