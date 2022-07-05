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
from PyQt5.QtWebEngineWidgets import *
from PyQt5 import QtWidgets


def main():
    app = QtWidgets.QApplication(sys.argv)
    from aas_editor.editorApp import EditorApp
    from aas_editor.splash import Splash
    splash = Splash()
    splash.show()

    window = EditorApp()
    window.show()

    splash.setFocus()

    app.exec_()


if __name__ == '__main__':
    main()
