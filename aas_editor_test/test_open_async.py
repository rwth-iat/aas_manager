import threading
import time
from pathlib import Path
from typing import Callable

# QtWebEngineWidgets must be imported before the QApplication exists (qapp fixture)
from PyQt6 import QtWebEngineWidgets  # noqa: F401
from PyQt6.QtCore import QModelIndex, QThreadPool
from PyQt6.QtWidgets import QMessageBox

from aas_editor_test.test_performance import newPackTreeView


def waitUntil(qapp, condition: Callable[[], bool], timeout: float = 10) -> bool:
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        qapp.processEvents()
        if condition():
            return True
        QThreadPool.globalInstance().waitForDone(10)
    return condition()


def openedFiles(view) -> set:
    from aas_editor.settings.app_settings import OPENED_FILES_ROLE

    return view.model().data(QModelIndex(), OPENED_FILES_ROLE)


class SlowPackage:
    """Wraps Package: records the calling thread and blocks until released."""

    def __init__(self, monkeypatch, failFirst: bool = False) -> None:
        import aas_editor.treeviews.treeview_pack as treeviewPack

        self.realPackage = treeviewPack.Package
        self.release = threading.Event()
        self.calls: list[tuple[threading.Thread, bool]] = []
        self.failFirst = failFirst
        monkeypatch.setattr(treeviewPack, "Package", self)

    def __call__(self, file, failsafe: bool = False):
        self.calls.append((threading.current_thread(), failsafe))
        self.release.wait(10)
        if self.failFirst and len(self.calls) == 1:
            raise ValueError("Malformed file")
        return self.realPackage(file, failsafe=failsafe)


class TestOpenPackInBackground:
    def test_open_returns_before_parsing_finishes(
        self, qapp, json_file: Path, monkeypatch
    ) -> None:
        slow = SlowPackage(monkeypatch)
        view = newPackTreeView()
        try:
            view.openPack(str(json_file))
            assert waitUntil(qapp, lambda: len(slow.calls) == 1)
            qapp.processEvents()
            assert openedFiles(view) == set()
        finally:
            slow.release.set()
        assert waitUntil(qapp, lambda: openedFiles(view) == {json_file.absolute()})

    def test_parse_runs_off_main_thread(
        self, qapp, json_file: Path, monkeypatch
    ) -> None:
        slow = SlowPackage(monkeypatch)
        slow.release.set()
        view = newPackTreeView()
        view.openPack(str(json_file))
        assert waitUntil(qapp, lambda: openedFiles(view) == {json_file.absolute()})
        assert slow.calls[0][0] is not threading.main_thread()

    def test_failure_asks_and_retries_failsafe(
        self, qapp, json_file: Path, monkeypatch
    ) -> None:
        slow = SlowPackage(monkeypatch, failFirst=True)
        slow.release.set()
        asked = []
        monkeypatch.setattr(
            QMessageBox, "exec",
            lambda box: asked.append(box.text()) or QMessageBox.StandardButton.Yes)
        view = newPackTreeView()
        view.openPack(str(json_file))
        assert waitUntil(qapp, lambda: openedFiles(view) == {json_file.absolute()})
        assert len(asked) == 1
        assert [failsafe for _, failsafe in slow.calls] == [False, True]

    def test_same_file_twice_while_loading_is_loaded_once(
        self, qapp, json_file: Path, monkeypatch
    ) -> None:
        slow = SlowPackage(monkeypatch)
        critical = []
        monkeypatch.setattr(
            QMessageBox, "critical", lambda *args: critical.append(args))
        view = newPackTreeView()
        try:
            view.openPack(str(json_file))
            view.openPack(str(json_file))
        finally:
            slow.release.set()
        assert waitUntil(qapp, lambda: openedFiles(view) == {json_file.absolute()})
        QThreadPool.globalInstance().waitForDone(5000)
        qapp.processEvents()
        assert len(slow.calls) == 1
        assert critical == []

    def test_real_file_is_opened_and_added_to_recent_files(
        self, qapp, json_file: Path
    ) -> None:
        from aas_editor.settings.app_settings import SETTINGS

        view = newPackTreeView()
        view.openPack(str(json_file))
        assert waitUntil(qapp, lambda: openedFiles(view) == {json_file.absolute()})
        assert SETTINGS.value("recentFiles", [])[0] == json_file.absolute().as_posix()
