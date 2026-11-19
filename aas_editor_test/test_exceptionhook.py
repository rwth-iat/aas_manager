import sys

import pytest


class FakeMessageBox:
    Icon = type("Icon", (), {"Critical": None})
    instances: list["FakeMessageBox"] = []

    def __init__(self, parent: object) -> None:
        self.detailedText = ""
        FakeMessageBox.instances.append(self)

    def setIcon(self, icon: object) -> None:
        pass

    def setText(self, text: str) -> None:
        pass

    def setDetailedText(self, text: str) -> None:
        self.detailedText = text

    def exec(self) -> int:
        return 0


def raiseBoom() -> None:
    raise ValueError("boom")


def test_crash_dialog_shows_formatted_traceback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # importing the module installs its excepthook; restore it after the test
    monkeypatch.setattr(sys, "excepthook", sys.excepthook)
    from aas_editor.utils import exceptionhook

    # an EditorApp from an earlier test may have registered its recovery save
    monkeypatch.setattr(exceptionhook, "_on_crash_callback", None)
    monkeypatch.setattr(exceptionhook.QtWidgets, "QMessageBox", FakeMessageBox)
    FakeMessageBox.instances.clear()
    try:
        raiseBoom()
    except ValueError:
        excInfo = sys.exc_info()

    with pytest.raises(SystemExit):
        exceptionhook.handle_exception(*excInfo)

    detailedText = FakeMessageBox.instances[-1].detailedText
    assert "<traceback object" not in detailedText
    assert "raiseBoom" in detailedText
    assert "ValueError: boom" in detailedText
    assert exceptionhook._handling_exception is False
