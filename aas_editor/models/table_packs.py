from typing import Any

from PyQt5.QtCore import QModelIndex, QVariant, Qt

from aas_editor.models import Package, StandardTable, QColor
from aas_editor.settings import PACKAGE_ROLE, NAME_ROLE


class PacksTable(StandardTable):
    def openedPacks(self):
        packs = set()
        for i in range(self.rowCount()):
            item = self.index(row=i)
            pack: Package = item.data(PACKAGE_ROLE)
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
        item = self.objByIndex(index)
        return item.data(role, index.column())

    def _getFgColor(self, index: QModelIndex):
        if self.objByIndex(index).new:
            color = QColor("green")
            return color
        elif self.objByIndex(index).changed:
            color = QColor(26, 13, 171)  # blue
            return color
        return QVariant()
