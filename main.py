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
import time

from PyQt6 import QtWidgets
from PyQt6.QtCore import QTimer
from aas_editor.utils import exceptionhook  # noqa: F401
from PyQt6 import QtWebEngineWidgets


def main():
    app = QtWidgets.QApplication(sys.argv)

    # Settings create Qt objects at import, so they load after QApplication
    from aas_editor.settings.app_settings import LOG_FILE
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    # force: importing aas_editor.settings already logs, installing a stderr handler
    logging.basicConfig(level=logging.INFO, filename=LOG_FILE, filemode="w",
                        force=True, format="%(asctime)s | %(levelname)s | %(message)s")

    from aas_editor.splash import newSplash, splashRemainingMs
    splash = newSplash()
    splash.show()
    splashShownAt = time.monotonic()
    app.processEvents()  # paint the splash before the slow imports below

    from aas_editor.settings.icons import initialize_all_icons
    # Initialize icons after QApp initialization to fix PyInstaller build errors.
    # QPixmap requires an active QApplication context; importing them earlier 
    # causes the application to crash during initialization.
    initialize_all_icons()

    from aas_editor.editorApp import EditorApp as CurrentApp
    from aas_editor.treeviews.treeview_pack import READ_POOL

    # Check if a file path is provided as an argument
    fileToOpen = sys.argv[1] if len(sys.argv) > 1 else None

    window = CurrentApp(fileToOpen)

    def showWindow():
        window.show()
        splash.finish(window)
        from aas_editor.update_check import askToCheckForUpdates, updateCheckDue
        if askToCheckForUpdates(window) and updateCheckDue():
            window.checkForUpdates()

    QTimer.singleShot(splashRemainingMs(splashShownAt, time.monotonic()), showWindow)

    app.exec()
    # A file still being read on quit: let its thread end before Python shuts down
    READ_POOL.waitForDone()


if __name__ == "__main__":
    main()
