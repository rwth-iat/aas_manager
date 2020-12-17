from typing import Any

from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QFont

from aas_editor.models import StandardTable
from aas_editor.package import Package
from aas_editor.settings.app_settings import PACKAGE_ROLE, DEFAULT_FONT, OPENED_PACKS_ROLE, OPENED_FILES_ROLE


class PacksTable(StandardTable):
    defaultFont = QFont(DEFAULT_FONT)

    def openedPacks(self):
        packs = set()
        for i in range(self.rowCount()):
            item = self.index(row=i)
            pack: Package = item.data(PACKAGE_ROLE)
            if pack:
                try:
                    packs.add(pack)
                except AttributeError:
                    continue
        return packs

    def openedFiles(self):
        files = set([pack.file for pack in self.openedPacks()])
        return files

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if role == Qt.ForegroundRole:
            return self._getFgColor(index)
        elif role == OPENED_PACKS_ROLE:
            return self.openedPacks()
        elif role == OPENED_FILES_ROLE:
            return self.openedFiles()
        else:
            return super(PacksTable, self).data(index, role)

