from typing import List, Union, Any

from PyQt5.QtCore import QAbstractProxyModel, QSortFilterProxyModel, QModelIndex, Qt, \
    QPersistentModelIndex
from PyQt5.QtGui import QBrush, QColor

from aas_editor.settings import HIGHLIGHT_YELLOW, ATTRIBUTE_COLUMN, VALUE_COLUMN, OBJECT_ROLE


class SearchProxyModel(QSortFilterProxyModel):
    def match(self, start: QModelIndex, role: int, value: Any, hits: int = ..., flags: Union[Qt.MatchFlags, Qt.MatchFlag] = ...) -> List[QModelIndex]:
        if role == OBJECT_ROLE:
            items = self.sourceModel().match(start, role, value, hits, flags)
            return [self.mapFromSource(item) for item in items]
        else:
            return super(SearchProxyModel, self).match(start, role, value, hits, flags)

    def setHighLightFilter(self, pattern: str,
                           filterColumns: List[int],
                           regExp: bool = True,
                           filter: bool = False,
                           matchCase: bool = False) -> List[QPersistentModelIndex]:
        for index in self.iterItems():
            self.setData(index, QBrush(QColor(0,0,0,0)), Qt.BackgroundRole)

        foundItems = []
        if not pattern:
            return foundItems

        if matchCase:
            self.setFilterCaseSensitivity(Qt.CaseSensitive)
        else:
            self.setFilterCaseSensitivity(Qt.CaseInsensitive)

        if regExp:
            self.setFilterRegExp(pattern)
        else:
            self.setFilterFixedString(pattern)

        for column in filterColumns:
            self.setFilterKeyColumn(column)

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
