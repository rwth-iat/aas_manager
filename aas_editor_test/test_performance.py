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


class TestExpectedMissesNotLogged:
    def test_opening_pack_logs_no_tracebacks(self, qapp, json_file: Path, caplog) -> None:
        view = newPackTreeView()
        caplog.clear()  # view init parses templates; only the pack open is under test
        with caplog.at_level(logging.DEBUG):
            openPack(view, json_file)
            qapp.processEvents()

        assert [r.getMessage() for r in caplog.records if r.exc_info] == []
