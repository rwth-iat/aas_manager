#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/

from typing import List, Any, Optional

from PyQt6.QtCore import QSortFilterProxyModel, QModelIndex, Qt, \
    QPersistentModelIndex, QObject, QAbstractItemModel


class SearchProxyModel(QSortFilterProxyModel):
    def __init__(self, sourceModel: QAbstractItemModel = None, parent: Optional[QObject] = None):
        super(SearchProxyModel, self).__init__(parent)
        if sourceModel:
            self.setSourceModel(sourceModel)

    def match(self, start: QModelIndex, role: int, value: Any, hits: int = ..., flags: Qt.MatchFlag = ...) -> List[QModelIndex]:
        items = self.sourceModel().match(start, role, value, hits, flags)
        return [self.mapFromSource(item) for item in items]

    def search(self, pattern: str,
               filterColumns: List[int],
               regExp: bool = True,
               filter: bool = False,
               matchCase: bool = False) -> List[QPersistentModelIndex]:
        foundItems = []
        if not pattern:
            return foundItems

        if matchCase:
            self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseSensitive)
        else:
            self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        if regExp:
            self.setFilterRegExp(pattern)
        else:
            self.setFilterFixedString(pattern)

        for column in filterColumns:
            self.setFilterKeyColumn(column)

            # save found items in column
            for index in self.iterItems():
                srcIndex = self.mapToSource(index.siblingAtColumn(column))
                foundItems.append(QPersistentModelIndex(srcIndex))

        if not filter:
            # show all items
            self.setFilterRegExp("")

        foundItems = [QPersistentModelIndex(self.mapFromSource(QModelIndex(i))) for i in foundItems]
        return foundItems

    def iterItems(self, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        def recurse(parent: QModelIndex):
            for row in range(self.rowCount(parent)):
                childIndex = self.index(row, 0, parent)
                yield childIndex
                if self.rowCount(childIndex):
                    yield from recurse(childIndex)
        yield from recurse(parent)
