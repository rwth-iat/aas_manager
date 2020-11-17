from typing import List

from PyQt5.QtCore import QAbstractProxyModel, QSortFilterProxyModel, QModelIndex, Qt, \
    QPersistentModelIndex
from PyQt5.QtGui import QBrush, QColor

from aas_editor.settings import HIGHLIGHT_YELLOW


class SearchProxyModel(QSortFilterProxyModel):
    def setHighLightFilter(self, pattern: str, regExp: bool = True,
                           filter: bool = False) -> List[QPersistentModelIndex]:
        for index in self.iterItems():
            self.setData(index, QBrush(QColor(0,0,0,0)), Qt.BackgroundRole)

        foundItems = []
        if not pattern:
            return foundItems

        if regExp:
            self.setFilterRegExp(pattern)
        else:
            self.setFilterFixedString(pattern)

        # paint Background of found items
        for index in self.iterItems():
            self.setData(index, QBrush(HIGHLIGHT_YELLOW), Qt.BackgroundRole)
            foundItems.append(QPersistentModelIndex(index))

        if not filter:
            # show all items
            self.setFilterRegExp("")
        return foundItems

    def iterItems(self, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        def recurse(parent: QModelIndex):
            for row in range(self.rowCount(parent)):
                childIndex = self.index(row, 0, parent)
                yield childIndex
                if self.rowCount(childIndex):
                    yield from recurse(childIndex)
        yield from recurse(parent)
