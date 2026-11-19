import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Callable

# QtWebEngineWidgets must be imported before the QApplication exists (qapp fixture)
from PyQt6 import QtWebEngineWidgets  # noqa: F401
from PyQt6.QtCore import QModelIndex
from PyQt6.QtWidgets import QMessageBox

from aas_editor_test.test_performance import newPackTreeView


def waitUntil(qapp, condition: Callable[[], bool], timeout: float = 10) -> bool:
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        qapp.processEvents()
        if condition():
            return True
        time.sleep(0.005)
    return condition()


def openedFiles(view) -> set:
    from aas_editor.settings.app_settings import OPENED_FILES_ROLE

    return view.model().data(QModelIndex(), OPENED_FILES_ROLE)


def runInSubprocess(code: str) -> subprocess.CompletedProcess:
    """Run a Qt snippet in its own process: a native crash must not kill pytest."""
    prelude = (
        "import sys, tempfile\n"
        "from PyQt6.QtCore import QSettings\n"
        "from PyQt6 import QtWebEngineWidgets\n"
        "from PyQt6.QtWidgets import QApplication, QMessageBox\n"
        "QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope,"
        " tempfile.mkdtemp())\n"
        "app = QApplication(sys.argv)\n"
        "import aas_editor.settings\n"
        "sys.excepthook = sys.__excepthook__\n"
        f"sys.path.insert(0, {str(Path(__file__).parent)!r})\n"
        "from test_open_async import waitUntil, openedFiles\n"
        "from test_performance import newPackTreeView\n"
    )
    return subprocess.run([sys.executable, "-c", prelude + code], capture_output=True,
                          text=True, timeout=120, cwd=Path(__file__).parent.parent)


class SlowPackage:
    """Wraps Package: records the calling thread and blocks until released."""

    def __init__(self, monkeypatch, failFirst: bool = False) -> None:
        import aas_editor.treeviews.treeview_pack as treeviewPack

        self.realPackage = treeviewPack.Package
        self.release = threading.Event()
        self.calls: list[tuple[threading.Thread, bool]] = []
        self.failFirst = failFirst
        monkeypatch.setattr(treeviewPack, "Package", self)

    def __call__(self, file: str, failsafe: bool = False):
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
        assert waitUntil(qapp, lambda: not view.loadingFiles())
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

    def test_path_object_is_opened(self, json_file: Path) -> None:
        # Session restore passes Path objects from the settings; subprocess
        # because a str-only signal emit fails in the reader thread and aborts
        result = runInSubprocess(
            "from pathlib import Path\n"
            "view = newPackTreeView()\n"
            f"file = Path({str(json_file)!r})\n"
            "view.openPack(file)\n"
            "assert waitUntil(app, lambda: openedFiles(view) == {file.absolute()})\n"
            "assert not view.loadingFiles()\n"
            "print('OK')\n")
        assert "OK" in result.stdout, result.stderr[-2000:]

    def test_already_opened_file_is_not_read_again(
        self, qapp, json_file: Path, monkeypatch
    ) -> None:
        slow = SlowPackage(monkeypatch)
        slow.release.set()
        critical = []
        monkeypatch.setattr(
            QMessageBox, "critical", lambda *args: critical.append(args[2]))
        view = newPackTreeView()
        view.openPack(str(json_file))
        assert waitUntil(qapp, lambda: openedFiles(view) == {json_file.absolute()})
        view.openPack(str(json_file))
        assert waitUntil(qapp, lambda: critical and not view.loadingFiles())
        assert len(slow.calls) == 1
        assert critical == [f"Package {json_file} is already opened"]

    def test_files_are_added_in_request_order(
        self, qapp, json_file: Path, tmp_path: Path, monkeypatch
    ) -> None:
        import aas_editor.treeviews.treeview_pack as treeviewPack

        files = [tmp_path / name for name in ("a.json", "b.json", "c.json")]
        for file in files:
            shutil.copy(json_file, file)
        realPackage = treeviewPack.Package
        delays = {"a.json": 0.4, "b.json": 0.2, "c.json": 0}

        def delayedPackage(file: str, failsafe: bool = False):
            time.sleep(delays[Path(file).name])
            return realPackage(file, failsafe=failsafe)

        monkeypatch.setattr(treeviewPack, "Package", delayedPackage)
        view = newPackTreeView()
        added = []
        realAdd = view.add_pack_to_tree
        monkeypatch.setattr(view, "add_pack_to_tree",
                            lambda pack: added.append(pack.file) or realAdd(pack))
        for file in files:
            view.openPack(str(file))
        assert waitUntil(qapp, lambda: len(openedFiles(view)) == 3)
        assert added == files

    def test_cancel_after_failure_clears_loading(
        self, qapp, json_file: Path, monkeypatch
    ) -> None:
        slow = SlowPackage(monkeypatch, failFirst=True)
        slow.release.set()
        monkeypatch.setattr(
            QMessageBox, "exec", lambda box: QMessageBox.StandardButton.Cancel)
        view = newPackTreeView()
        view.openPack(str(json_file))
        assert waitUntil(qapp, lambda: not view.loadingFiles())
        assert view._loadProgress is None
        assert openedFiles(view) == set()
        assert len(slow.calls) == 1

    def test_second_failure_shows_error_and_drops_recent_file(
        self, qapp, tmp_path: Path, monkeypatch
    ) -> None:
        from aas_editor.settings.app_settings import SETTINGS

        broken = (tmp_path / "broken.json").absolute()
        broken.write_text("not json")
        shown = []
        monkeypatch.setattr(
            QMessageBox, "exec",
            lambda box: shown.append(box.text()) or QMessageBox.StandardButton.Yes)
        view = newPackTreeView()
        view.updateRecentFiles(broken.as_posix())
        view.openPack(broken.as_posix())
        assert waitUntil(qapp, lambda: not view.loadingFiles())
        assert len(shown) == 2
        assert shown[1].startswith(f"Package {broken.as_posix()} couldn't be opened")
        assert broken.as_posix() not in SETTINGS.value("recentFiles", [])


class TestReadCrashSafety:
    """Run in a subprocess: these used to kill the whole process."""

    def test_deeply_nested_json_ends_in_failure_path(self, tmp_path: Path) -> None:
        deep = tmp_path / "deep.json"
        deep.write_text('{"submodels": ' + "[" * 5000 + "]" * 5000 + "}")
        result = runInSubprocess(
            "shown = []\n"
            "QMessageBox.exec = lambda box: shown.append(box.text())"
            " or QMessageBox.StandardButton.Cancel\n"
            "view = newPackTreeView()\n"
            f"view.openPack({str(deep)!r})\n"
            "assert waitUntil(app, lambda: not view.loadingFiles())\n"
            "print('SHOWN', shown)\n")
        assert result.returncode == 0, result.stderr[-2000:]
        assert "SHOWN ['Error while reading package" in result.stdout

    def test_base_exception_in_reader_does_not_leave_loading_stuck(
        self, json_file: Path
    ) -> None:
        result = runInSubprocess(
            "import aas_editor.treeviews.treeview_pack as treeviewPack\n"
            "class Boom(BaseException):\n"
            "    pass\n"
            "def boom(file, failsafe=False):\n"
            "    raise Boom()\n"
            "treeviewPack.Package = boom\n"
            "shown = []\n"
            "QMessageBox.exec = lambda box: shown.append(box.text())"
            " or QMessageBox.StandardButton.Yes\n"
            "view = newPackTreeView()\n"
            f"view.openPack({str(json_file)!r})\n"
            "assert waitUntil(app, lambda: not view.loadingFiles(), timeout=10)\n"
            "print('SHOWN', len(shown))\n")
        assert result.returncode == 0, result.stderr[-2000:]
        assert "SHOWN 2" in result.stdout
