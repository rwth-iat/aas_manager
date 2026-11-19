import logging
from pathlib import Path

# QtWebEngineWidgets must be imported before the QApplication exists (qapp fixture)
from PyQt6 import QtWebEngineWidgets  # noqa: F401
from PyQt6.QtCore import QModelIndex


def newPackTreeView():
    from aas_editor.models import PacksTable, PackTreeViewItem
    from aas_editor.settings.app_settings import DEFAULT_COLUMNS_IN_PACKS_TABLE
    from aas_editor.treeviews.treeview_pack import PackTreeView

    view = PackTreeView()
    view.setModelWithProxy(PacksTable(list(DEFAULT_COLUMNS_IN_PACKS_TABLE), PackTreeViewItem(None, None)))
    return view


def openPack(view, jsonFile: Path):
    from aas_editor.package import Package

    view.add_pack_to_tree(Package(jsonFile))
    view.expandAll()
    view.show()
    return view, view.model()


def openedTreeView(jsonFile: Path):
    return openPack(newPackTreeView(), jsonFile)


class TestIdleRepaint:
    def test_current_row_does_not_emit_data_changed_while_idle(self, qapp, json_file: Path) -> None:
        view, model = openedTreeView(json_file)
        view.setCurrentIndex(model.index(0, 0, model.index(0, 0)))
        qapp.processEvents()
        emitted = []
        model.dataChanged.connect(lambda *args: emitted.append(args))

        # Bounded, not timed: long event pumping trips a QtWebEngine crash under offscreen
        for _ in range(20):
            qapp.processEvents()

        assert emitted == []


class TestInitParamsCache:
    def test_init_signature_inspected_once_per_type(self, qapp, monkeypatch) -> None:
        import inspect
        from basyx.aas.model import Range
        from aas_editor.utils.util import getParamsAndTypehints4init

        calls = []
        realGetfullargspec = inspect.getfullargspec
        monkeypatch.setattr(inspect, "getfullargspec", lambda f: calls.append(f) or realGetfullargspec(f))

        getParamsAndTypehints4init(Range)
        getParamsAndTypehints4init(Range)

        assert len(calls) <= 1

    def test_results_are_independent_copies(self, qapp) -> None:
        from basyx.aas.model import Range
        from aas_editor.utils.util import getReqParams4init

        first = getReqParams4init(Range, rmDefParams=True)
        first.clear()

        assert getReqParams4init(Range, rmDefParams=True)


class TestAttrDocCache:
    def test_docstring_parsed_once_per_class_and_attr(self, qapp, monkeypatch) -> None:
        import re
        from basyx.aas.model import Property
        from aas_editor.utils.util import getAttrDoc

        calls = []
        realSearch = re.search
        def countingSearch(*args, **kwargs):
            calls.append(args)
            return realSearch(*args, **kwargs)

        monkeypatch.setattr(re, "search", countingSearch)

        first = Property("p1", "xs:string")
        second = Property("p2", "xs:string")
        assert getAttrDoc("value", first) == getAttrDoc("value", second)

        assert len(calls) <= 1

    def test_results_unchanged(self, qapp) -> None:
        from basyx.aas.model import Property, Submodel
        from aas_editor.utils.util import getAttrDoc

        prop = Property("p1", "xs:string")
        assert getAttrDoc("value", prop) == (
            "value:  The value of the property instance. ")
        assert getAttrDoc("id_short", prop) == (
            "id_short:  Identifying string of the element within its name space.  ")
        assert getAttrDoc("semantic_id", Property).startswith(
            "semantic_id:  Identifier of the semantic definition of the element.")
        assert getAttrDoc("submodel_element", Submodel) == (
            "submodel_element:  Unordered list of SubmodelElements  ")
        assert getAttrDoc("value", None, Property.__doc__) == getAttrDoc("value", prop)
        assert getAttrDoc("nonexistent", prop) == ""
        assert getAttrDoc("value", None) == ""
        assert getAttrDoc("value", None, "") == ""


class TestExpectedMissesNotLogged:
    def test_opening_pack_logs_no_tracebacks(self, qapp, json_file: Path, caplog) -> None:
        view = newPackTreeView()
        caplog.clear()  # view init parses templates; only the pack open is under test
        with caplog.at_level(logging.DEBUG):
            openPack(view, json_file)
            qapp.processEvents()

        assert [r.getMessage() for r in caplog.records if r.exc_info] == []


class TestPaintCost:
    def test_index_lookup_does_not_count_rows(
            self, qapp, json_file: Path, monkeypatch) -> None:
        # The proxy maps every role requested at paint to a source index() call
        from aas_editor.models.table_standard import StandardTable

        view, model = openedTreeView(json_file)
        qapp.processEvents()
        realRowCount = StandardTable.rowCount
        realIndex = StandardTable.index
        rowCountCalls = []
        indexCalls = []
        monkeypatch.setattr(StandardTable, "rowCount",
                            lambda *a: rowCountCalls.append(a) or realRowCount(*a))
        monkeypatch.setattr(StandardTable, "index",
                            lambda *a: indexCalls.append(a) or realIndex(*a))

        view.viewport().repaint()

        assert indexCalls
        assert rowCountCalls == []

    def test_index_bounds_unchanged(self, qapp, json_file: Path) -> None:
        view, proxy = openedTreeView(json_file)
        model = proxy.sourceModel()
        rows = model.rowCount()
        columns = model.columnCount()

        assert model.index(0, 0).isValid()
        assert model.index(rows - 1, columns - 1).isValid()
        assert not model.index(rows, 0).isValid()
        assert not model.index(-1, 0).isValid()
        assert not model.index(0, columns).isValid()
        assert not model.index(0, -1).isValid()
        item = model.index(0, 0).internalPointer()
        assert model.index(0, 1).internalPointer() is item

    def test_flags_of_fixed_columns_do_not_render_display_text(
            self, qapp, json_file: Path, monkeypatch) -> None:
        from PyQt6.QtCore import Qt
        from aas_editor.models.item_standard import StandardItem

        view, proxy = openedTreeView(json_file)
        model = proxy.sourceModel()
        index = model.index(0, 0, model.index(0, 0))
        realData = StandardItem.data
        displayCalls = []

        def countingData(self, role, *args, **kwargs):
            if role == Qt.ItemDataRole.DisplayRole:
                displayCalls.append(args)
            return realData(self, role, *args, **kwargs)

        monkeypatch.setattr(StandardItem, "data", countingData)

        for column in range(model.columnCount()):
            model.flags(index.siblingAtColumn(column))

        assert displayCalls == []

    def test_flags_unchanged(self, qapp, json_file: Path) -> None:
        from PyQt6.QtCore import Qt
        from aas_editor.models.table_standard import StandardTable

        view, proxy = openedTreeView(json_file)
        model = proxy.sourceModel()
        # Extra attribute columns: one present on items, one missing everywhere
        model._columns = (*model._columns, "id_short", "no_such_attr")
        Flag = Qt.ItemFlag
        editable = Flag.ItemIsEditable | Flag.ItemIsEnabled | Flag.ItemIsSelectable

        def legacyFlags(index: QModelIndex) -> Qt.ItemFlag:
            if not index.isValid() or index.data(Qt.ItemDataRole.DisplayRole) is None:
                return Flag.NoItemFlags
            if index.column() in (2, 3):
                return Flag.ItemIsEnabled | Flag.ItemIsSelectable
            return editable

        indexes = [QModelIndex()]
        for rowIndex in model.iterItems():
            indexes += [rowIndex.siblingAtColumn(c) for c in range(model.columnCount())]
        flags = [StandardTable.flags(model, i) for i in indexes]

        assert flags == [legacyFlags(i) for i in indexes]
        assert Flag.NoItemFlags in flags and editable in flags
