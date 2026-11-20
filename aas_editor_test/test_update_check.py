# QtWebEngineWidgets must be imported before the QApplication exists (qapp)
from PyQt6 import QtWebEngineWidgets  # noqa: F401
import json
from pathlib import Path

import pytest

from aas_editor_test.test_open_async import waitUntil


def releaseFile(tmp_path: Path, tag: str) -> str:
    """GitHub 'latest release' answer as a local file URL."""
    file = tmp_path / "latest.json"
    file.write_text(json.dumps({"tag_name": tag, "html_url": "https://example.org/r"}))
    return file.as_uri()


@pytest.mark.parametrize("latest, current, newer", [
    ("0.5.1", "0.5.0", True),
    ("0.5.0", "0.5.0", False),
    ("0.10.0", "0.9.9", True),
    ("0.4.13", "0.5.0", False),
])
def test_is_newer_compares_numerically(qapp, latest, current, newer) -> None:
    from aas_editor.update_check import isNewer

    assert isNewer(latest, current) is newer


def test_latest_release_reads_tag_and_page(qapp, tmp_path) -> None:
    from aas_editor.update_check import Release, latestRelease

    url = releaseFile(tmp_path, "v9.9.9")
    assert latestRelease(url) == Release("9.9.9", "https://example.org/r")


@pytest.mark.parametrize("content", ["not json", '{"no": "tag"}',
                                     '{"tag_name": "v1.x", "html_url": "u"}'])
def test_latest_release_is_none_on_bad_answer(qapp, tmp_path, content) -> None:
    from aas_editor.update_check import latestRelease

    file = tmp_path / "latest.json"
    file.write_text(content)
    assert latestRelease(file.as_uri()) is None


def test_latest_release_is_none_when_unreachable(qapp, tmp_path) -> None:
    from aas_editor.update_check import latestRelease

    assert latestRelease((tmp_path / "missing.json").as_uri()) is None


def test_checker_reports_release_in_gui_thread(qapp, tmp_path) -> None:
    from aas_editor.update_check import Release, UpdateChecker

    results = []
    checker = UpdateChecker(releaseFile(tmp_path, "v9.9.9"))
    checker.finished.connect(results.append)
    checker.start()
    assert waitUntil(qapp, lambda: results != [], timeout=5)
    assert results == [Release("9.9.9", "https://example.org/r")]


@pytest.fixture
def unsetCheckSetting(qapp):
    from aas_editor.settings.app_settings import SETTINGS, AppSettings

    SETTINGS.remove(AppSettings.CHECK_FOR_UPDATES.name)
    yield AppSettings.CHECK_FOR_UPDATES
    SETTINGS.remove(AppSettings.CHECK_FOR_UPDATES.name)


@pytest.mark.parametrize("answer, enabled", [("Yes", True), ("No", False)])
def test_first_start_asks_and_stores_answer(unsetCheckSetting, monkeypatch,
                                            answer, enabled) -> None:
    from PyQt6.QtWidgets import QMessageBox

    from aas_editor.update_check import askToCheckForUpdates

    asked = []

    def question(*args, **kwargs):
        asked.append(args)
        return getattr(QMessageBox.StandardButton, answer)

    monkeypatch.setattr(QMessageBox, "question", question)
    assert not unsetCheckSetting.isSet()
    assert askToCheckForUpdates(None) is enabled
    assert unsetCheckSetting.isSet()
    assert unsetCheckSetting.value() is enabled
    assert askToCheckForUpdates(None) is enabled  # answered: not asked again
    assert len(asked) == 1


class FakeWindow:
    """Only what EditorApp.showUpdateResult touches: no full main window needed."""
    def __init__(self):
        from PyQt6.QtWidgets import QLabel

        self._updateLabel = QLabel()
        self._updateLabel.hide()


@pytest.fixture
def infoBoxes(monkeypatch):
    from PyQt6.QtWidgets import QMessageBox

    texts = []
    monkeypatch.setattr(QMessageBox, "information",
                        lambda parent, title, text: texts.append(text))
    return texts


@pytest.mark.parametrize("manual", [True, False])
def test_newer_release_shows_download_link(qapp, infoBoxes, manual) -> None:
    from aas_editor.editorApp import EditorApp
    from aas_editor.update_check import Release

    window = FakeWindow()
    EditorApp.showUpdateResult(window, Release("99.0.0", "https://example.org/r"),
                               manual)
    assert not window._updateLabel.isHidden()
    assert "https://example.org/r" in window._updateLabel.text()
    assert len(infoBoxes) == (1 if manual else 0)


@pytest.mark.parametrize("release, message", [
    (None, "Could not reach GitHub"),
    ("current", "latest version"),
])
def test_no_update_answers_only_manual_check(qapp, infoBoxes, release,
                                             message) -> None:
    from aas_editor.editorApp import EditorApp
    from aas_editor.settings.app_settings import VERSION
    from aas_editor.update_check import Release

    if release == "current":
        release = Release(VERSION, "https://example.org/r")
    window = FakeWindow()
    EditorApp.showUpdateResult(window, release, manual=False)
    assert infoBoxes == []
    EditorApp.showUpdateResult(window, release, manual=True)
    assert message in infoBoxes[0]
    assert window._updateLabel.isHidden()


@pytest.fixture
def noLastCheck(qapp):
    from aas_editor.settings.app_settings import SETTINGS, AppSettings

    SETTINGS.remove(AppSettings.LAST_UPDATE_CHECK.name)
    yield
    SETTINGS.remove(AppSettings.LAST_UPDATE_CHECK.name)


def test_check_is_due_at_most_once_a_day(noLastCheck) -> None:
    from aas_editor.update_check import updateCheckDue

    day = 24 * 3600
    start = 1.8e9  # 2027
    assert updateCheckDue(now=start)  # never checked
    assert not updateCheckDue(now=start + day - 1)
    assert updateCheckDue(now=start + day)
    assert not updateCheckDue(now=start + day + 1)
