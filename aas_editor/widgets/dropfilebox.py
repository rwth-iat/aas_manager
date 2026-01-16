#  Copyright (C) 2025  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QDropEvent, QDragEnterEvent


class DropFileQWebEngineView(QWebEngineView):
    fileDropped = pyqtSignal(str)

    def __init__(self, parent=None, emptyViewMsg=None, description=None):
        super().__init__(parent)
        # Write empty view message with the small svg in the center and with the description below
        svg = r'<svg xmlns="http://www.w3.org/2000/svg" id="mdi-open-in-app" viewBox="0 0 24 24"><path d="M12,10L8,14H11V20H13V14H16M19,4H5C3.89,4 3,4.9 3,6V18A2,2 0 0,0 5,20H9V18H5V8H19V18H15V20H19A2,2 0 0,0 21,18V6A2,2 0 0,0 19,4Z" /></svg>'
        self.setHtml(f"""
        <div style="display:flex;flex-direction:column;justify-content:center;align-items:center;height:100%;">
            <div style="width:50px;height:50px;margin-bottom:20px;">{svg}</div>
            <div style="text-align:center;">{emptyViewMsg}</div>
            <div style="text-align:center;">{description or ""}</div>
        </div>
        """)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls:
            event.accept()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()

    def dropEvent(self, e: QDropEvent) -> None:
        for url in e.mimeData().urls():
            file = str(url.toLocalFile())
            self.fileDropped.emit(file)
