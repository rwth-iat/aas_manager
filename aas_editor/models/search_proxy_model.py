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

from typing import Any, Iterator, List, Optional, Tuple

from PyQt6.QtCore import QSortFilterProxyModel, QModelIndex, Qt, \
    QPersistentModelIndex, QObject, QAbstractItemModel, QRegularExpression
from PyQt6.QtGui import QBrush

from aas_editor.settings.colors import HIGHLIGHT_YELLOW


class SearchProxyModel(QSortFilterProxyModel):
    def __init__(self, sourceModel: QAbstractItemModel = None, parent: Optional[QObject] = None):
        super(SearchProxyModel, self).__init__(parent)
        # Rows with a matching descendant stay visible in filter mode
        self.setRecursiveFilteringEnabled(True)
        self._filterRegex: Optional[QRegularExpression] = None
        self._filterColumns: List[int] = []
        # Highlight is computed on paint, so it stays right after sort/insert/remove
        self._highlightRegex: Optional[QRegularExpression] = None
        self._highlightColumns: List[int] = []
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
        """Return the matching cells in view order; hide the rest if filter is set."""
        regex = self._regex(pattern, regExp, matchCase)
        self._setFilter(regex if filter else None, filterColumns)
        self._highlightRegex = regex
        self._highlightColumns = list(filterColumns)
        if regex is None or self.sourceModel() is None:
            return []

        foundItems = []
        for index in self._iterSourceRows():
            for column in filterColumns:
                cell = index.siblingAtColumn(column)
                if self._matches(regex, cell):
                    foundItems.append(self.mapFromSource(cell))
        # The view may sort: order hits as the user sees them
        foundItems.sort(key=treePath)
        return [QPersistentModelIndex(index) for index in foundItems]

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role == Qt.ItemDataRole.BackgroundRole and self._highlightRegex is not None \
                and index.column() in self._highlightColumns \
                and self._matches(self._highlightRegex, index):
            return QBrush(HIGHLIGHT_YELLOW)
        return super().data(index, role)

    @staticmethod
    def _regex(pattern: str, regExp: bool, matchCase: bool) -> Optional[QRegularExpression]:
        if not pattern:
            return None
        if not regExp:
            pattern = QRegularExpression.escape(pattern)
        options = QRegularExpression.PatternOption.NoPatternOption if matchCase \
            else QRegularExpression.PatternOption.CaseInsensitiveOption
        regex = QRegularExpression(pattern, options)
        # An unfinished regex while typing finds nothing instead of failing
        return regex if regex.isValid() else None

    @staticmethod
    def _matches(regex: QRegularExpression, index: QModelIndex) -> bool:
        text = index.data(Qt.ItemDataRole.DisplayRole)
        return text is not None and regex.match(str(text)).hasMatch()

    def _setFilter(self, regex: Optional[QRegularExpression], columns: List[int]) -> None:
        # Refilter only on change: each refilter walks the whole tree
        if self._filterKey(regex, columns) == self._filterKey(self._filterRegex, self._filterColumns):
            return
        self._filterRegex = regex
        self._filterColumns = list(columns)
        self.invalidateRowsFilter()

    @staticmethod
    def _filterKey(regex: Optional[QRegularExpression], columns: List[int]) -> Optional[tuple]:
        return (regex.pattern(), regex.patternOptions(), tuple(columns)) \
            if regex is not None else None

    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex) -> bool:
        if self._filterRegex is None:
            return True
        model = self.sourceModel()
        return any(self._matches(self._filterRegex, model.index(sourceRow, column, sourceParent))
                   for column in self._filterColumns)

    def iterItems(self, parent: QModelIndex = QModelIndex()) -> Iterator[QModelIndex]:
        """Visible rows in view order (used by main_test.py)."""
        for row in range(self.rowCount(parent)):
            index = self.index(row, 0, parent)
            yield index
            yield from self.iterItems(index)

    def _iterSourceRows(self, parent: QModelIndex = QModelIndex()) -> Iterator[QModelIndex]:
        """Source rows in tree order (pre-order), hidden rows included."""
        model = self.sourceModel()
        for row in range(model.rowCount(parent)):
            index = model.index(row, 0, parent)
            yield index
            yield from self._iterSourceRows(index)


def treePath(index: QModelIndex) -> Tuple[int, ...]:
    """Row numbers from the root: tuples compare in tree (pre-)order."""
    path = []
    while index.isValid():
        path.append(index.row())
        index = index.parent()
    return tuple(reversed(path))
