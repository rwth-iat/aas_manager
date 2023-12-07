#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/

import sys
import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import *
from PyQt5 import QtWidgets
from aas_editor.utils import exceptionhook

logging.basicConfig(level=logging.INFO, filename="log.log", filemode="w",
                    format="%(asctime)s | %(levelname)s | %(message)s")


def main():
    app = QtWidgets.QApplication(sys.argv)
    from aas_editor.editorApp import EditorApp as CurrentApp

    # Check if a file path is provided as an argument
    fileToOpen = sys.argv[1] if len(sys.argv) > 1 else None

    window = CurrentApp(fileToOpen)

    window.show()

    # splash.setFocus()
    app.exec_()


if __name__ == '__main__':
    main()
