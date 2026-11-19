import logging
from typing import List

import pytest
from PyQt6.QtCore import QModelIndex, QPersistentModelIndex, Qt
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QWidget

from aas_editor_test.test_open_async import waitUntil


def row(*names: str) -> List[QStandardItem]:
    return [QStandardItem(name) for name in names]


def newModel() -> QStandardItemModel:
    """Tree: fruits/[apple, berries/[pineapple, cherry]], stones/[rock, pebble]."""
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(["Name", "Value"])
    fruits = row("fruits", "food")
    berries = row("berries", "small")
    berries[0].appendRow(row("pineapple", "big"))
    berries[0].appendRow(row("cherry", "apple-red"))
    fruits[0].appendRow(row("apple", "red"))
    fruits[0].appendRow(berries)
    stones = row("stones", "")
    stones[0].appendRow(row("rock", "grey"))
    stones[0].appendRow(row("pebble", "grey"))
    model.appendRow(fruits)
    model.appendRow(stones)
    return model


@pytest.fixture
def view(qapp):
    from aas_editor.treeviews.base import TreeView

    view = TreeView()
    view.testModel = newModel()  # the proxy does not own its source model
    view.setModelWithProxy(view.testModel)
    view.sortByColumn(0, Qt.SortOrder.AscendingOrder)
    view.expandAll()
    return view


@pytest.fixture
def bar(view):
    from aas_editor.widgets.search import SearchBar

    view.testParent = QWidget()  # keep the bar's parent alive
    return SearchBar(view, filterColumns=[0, 1], parent=view.testParent)


def names(indexes: List[QPersistentModelIndex]) -> List[str]:
    return [QModelIndex(i).data() for i in indexes]


def visibleNames(view) -> List[str]:
    model = view.model()
    result = []

    def walk(parent: QModelIndex) -> None:
        for r in range(model.rowCount(parent)):
            index = model.index(r, 0, parent)
            result.append(index.data())
            walk(index)

    walk(QModelIndex())
    return result


def search(view, pattern: str, columns=(0,), **kwargs) -> List[str]:
    return names(view.model().search(pattern, filterColumns=list(columns), **kwargs))


class TestSearchProxyModel:
    def test_only_matching_items_in_tree_order(self, view) -> None:
        # Parents of matches ("fruits", "berries") are not hits
        assert search(view, "apple", regExp=False) == ["apple", "pineapple"]

    def test_filter_keeps_matches_and_their_parents(self, view) -> None:
        search(view, "apple", filter=True, regExp=False)
        assert visibleNames(view) == ["fruits", "apple", "berries", "pineapple"]

    def test_filter_matches_any_searched_column(self, view) -> None:
        # "cherry" matches in column 1 only, "apple" and "pineapple" in column 0
        hits = search(view, "apple", columns=(0, 1), filter=True, regExp=False)
        assert hits == ["apple", "apple-red", "pineapple"]
        assert visibleNames(view) == ["fruits", "apple", "berries", "cherry",
                                      "pineapple"]

    def test_hits_follow_view_sort_order(self, view) -> None:
        view.sortByColumn(0, Qt.SortOrder.DescendingOrder)
        assert search(view, "apple", regExp=False) == ["pineapple", "apple"]

    def test_empty_pattern_shows_all(self, view) -> None:
        search(view, "apple", filter=True)
        assert search(view, "", filter=True) == []
        assert len(visibleNames(view)) == 8

    def test_case_and_regex(self, view) -> None:
        assert search(view, "APPLE", regExp=False) == ["apple", "pineapple"]
        assert search(view, "APPLE", regExp=False, matchCase=True) == []
        assert search(view, "^p", regExp=True) == ["pineapple", "pebble"]
        assert search(view, "^p", regExp=False) == []

    def test_invalid_regex_finds_nothing_and_hides_nothing(self, view) -> None:
        assert search(view, "(", regExp=True, filter=True) == []
        assert len(visibleNames(view)) == 8


class TestSearchBar:
    def test_typing_searches_after_pause(self, qapp, bar) -> None:
        bar.searchLine.setText("apple")
        assert bar.foundItems == []
        assert waitUntil(qapp, lambda: bar.foundItems != [], timeout=2)
        assert names(bar.foundItems) == ["apple", "apple-red", "pineapple"]

    def test_filtering_does_not_move_current_item(self, bar, view) -> None:
        current = view.model().index(1, 0)  # "stones"
        view.setCurrentIndex(current)
        bar.filterBtn.setChecked(True)
        bar.searchLine.setText("rock")
        bar.search()
        # Only "stones" ancestors stay; rows of "fruits" were filtered out
        assert visibleNames(view) == ["stones", "rock"]
        assert view.currentIndex().data() == "rock"

    def test_adding_a_filtered_out_row_keeps_current_item(self, bar, view) -> None:
        bar.filterBtn.setChecked(True)
        bar.searchLine.setText("rock")
        bar.search()
        source = view.sourceModel()
        source.itemFromIndex(source.index(1, 0)).appendRow(row("sand"))
        assert view.currentIndex().data() == "rock"

    def test_search_without_source_model_finds_nothing(self, qapp) -> None:
        from aas_editor.models.search_proxy_model import SearchProxyModel

        assert SearchProxyModel().search("x", filterColumns=[0]) == []

    def test_removing_a_row_still_selects_its_parent(self, view) -> None:
        source = view.sourceModel()
        stones = source.index(1, 0)
        view.setCurrentIndex(view.model().mapFromSource(source.index(0, 0, stones)))
        source.removeRow(0, stones)
        assert view.currentIndex().data() == "stones"

    def test_next_and_previous_follow_tree_order_past_100_children(
        self, qapp
    ) -> None:
        from aas_editor.treeviews.base import TreeView
        from aas_editor.widgets.search import SearchBar

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Name"])
        first = row("first")
        for i in range(150):
            first[0].appendRow(row(f"item{i}"))
        model.appendRow(first)
        model.appendRow(row("item-last"))
        view = TreeView()
        view.setModelWithProxy(model)
        view.setSortingEnabled(False)
        view.model().sort(-1)  # source order: item0 .. item149
        parent = QWidget()
        bar = SearchBar(view, filterColumns=[0], parent=parent)
        bar.searchLine.setText("item")
        bar.search()

        visited = [view.currentIndex().data()]
        for _ in range(150):
            bar.next()
            visited.append(view.currentIndex().data())
        assert visited == [f"item{i}" for i in range(150)] + ["item-last"]
        bar.previous()
        assert view.currentIndex().data() == "item149"

    def test_next_follows_new_sort_order_after_search(self, bar, view) -> None:
        bar.searchLine.setText("apple")
        bar.search()  # ascending: apple, apple-red, pineapple
        view.sortByColumn(0, Qt.SortOrder.DescendingOrder)
        view.setCurrentIndex(view.model().index(0, 0))  # "stones", first row now
        visited = []
        for _ in range(3):
            bar.next()
            visited.append(view.currentIndex().data())
        assert visited == ["pineapple", "apple-red", "apple"]

    def test_next_does_not_log(self, bar, caplog) -> None:
        bar.searchLine.setText("apple")
        bar.search()
        with caplog.at_level(logging.DEBUG):
            bar.next()
            bar.previous()
        assert caplog.records == []
