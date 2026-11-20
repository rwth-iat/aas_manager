#  Copyright (C) 2026  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
"""Check GitHub for a newer release; the user downloads and installs it."""
import json
import logging
import ssl
import threading
import time
import urllib.request
from collections import namedtuple
from typing import Optional, Tuple

import certifi

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QWidget

from aas_editor.settings.app_settings import (APPLICATION_LINK, APPLICATION_NAME,
                                              VERSION, AppSettings)

RELEASES_API = (f"{APPLICATION_LINK.replace('github.com/', 'api.github.com/repos/')}"
                f"/releases/latest")
# Python has no system CA certificates on macOS and in the PyInstaller build
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
Release = namedtuple("Release", ("version", "url"))
DAY_SECONDS = 24 * 3600


def versionTuple(version: str) -> Tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def isNewer(latest: str, current: str) -> bool:
    return versionTuple(latest) > versionTuple(current)


def latestRelease(url: str = RELEASES_API) -> Optional[Release]:
    """Latest published release, or None if it cannot be read."""
    request = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": f"AAS-Manager/{VERSION}",
    })
    try:
        with urllib.request.urlopen(request, timeout=10, context=SSL_CONTEXT) as answer:
            data = json.load(answer)
        release = Release(data["tag_name"].removeprefix("v"), data["html_url"])
        versionTuple(release.version)
        return release
    except (OSError, ValueError, KeyError, TypeError) as e:
        logging.info(f"Update check failed: {e}")
        return None


def updateCheckDue(now: Optional[float] = None) -> bool:
    """True at most once a day; remembers when it was last true."""
    now = time.time() if now is None else now
    if now - AppSettings.LAST_UPDATE_CHECK.value() < DAY_SECONDS:
        return False
    AppSettings.LAST_UPDATE_CHECK.setValue(now)
    return True


class UpdateChecker(QObject):
    """Reads the latest release in a thread, reports it in the GUI thread."""
    finished = pyqtSignal(object)  # Release or None

    def __init__(self, url: str = RELEASES_API, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.url = url

    def start(self) -> None:
        threading.Thread(target=lambda: self.finished.emit(latestRelease(self.url)),
                         daemon=True).start()


def askToCheckForUpdates(parent: Optional[QWidget]) -> bool:
    """Whether to check on start; asks the user once, on the first start."""
    setting = AppSettings.CHECK_FOR_UPDATES
    if not setting.isSet():
        answer = QMessageBox.question(
            parent, "Check for Updates",
            f"Should {APPLICATION_NAME} check for a new version once a day on start?\n\n"
            f"It asks GitHub for the latest release; nothing else is sent.\n"
            f"You can change this later in Settings.")
        setting.setValue(answer == QMessageBox.StandardButton.Yes)
    return setting.value()
