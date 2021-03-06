from typing import List, Union, Any, Optional

from PyQt5.QtCore import QSortFilterProxyModel, QModelIndex, Qt, \
    QPersistentModelIndex, QObject, QAbstractItemModel
from PyQt5.QtGui import QBrush, QColor

from aas_editor.settings.app_settings import OBJECT_ROLE


class SearchProxyModel(QSortFilterProxyModel):
    def __init__(self, sourceModel: QAbstractItemModel = None, parent: Optional[QObject] = None):
        super(SearchProxyModel, self).__init__(parent)
        if sourceModel:
            self.setSourceModel(sourceModel)

    def match(self, start: QModelIndex, role: int, value: Any, hits: int = ..., flags: Union[Qt.MatchFlags, Qt.MatchFlag] = ...) -> List[QModelIndex]:
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
            self.setFilterCaseSensitivity(Qt.CaseSensitive)
        else:
            self.setFilterCaseSensitivity(Qt.CaseInsensitive)

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
