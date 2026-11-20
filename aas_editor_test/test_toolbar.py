# QtWebEngineWidgets must be imported before the QApplication exists (qapp)
from PyQt6 import QtWebEngineWidgets  # noqa: F401
from typing import List

import pytest
from PyQt6.QtGui import QAction


@pytest.fixture
def buttonsSetting(qapp):
    from aas_editor.settings.app_settings import SETTINGS, Setting

    setting = Setting("testToolbarHiddenButtons", ["B"], list)
    SETTINGS.remove(setting.name)
    yield setting
    SETTINGS.remove(setting.name)


@pytest.fixture
def toolBar(qapp):
    from aas_editor.widgets.toolbar import ToolBar

    bar = ToolBar(None)
    bar.testActions = {name: QAction(name, bar) for name in "ABCD"}
    bar.addButton(bar.testActions["A"], "A")
    bar.addButton(bar.testActions["B"], "B")
    bar.addSeparator()
    bar.addButton(bar.testActions["C"], "C")
    bar.addButton(bar.testActions["D"], "D")
    return bar


def shown(bar) -> List[str]:
    return ["|" if a.isSeparator() else a.text() for a in bar.actions()]


def menuEntries(menu) -> dict:
    return {a.text(): a for a in menu.actions()}


def test_buttons_hidden_by_default_setting(toolBar, buttonsSetting) -> None:
    menu = toolBar.buttonsMenu("Buttons", buttonsSetting)
    assert shown(toolBar) == ["A", "|", "C", "D"]
    assert {name: a.isChecked() for name, a in menuEntries(menu).items()} == \
        {"A": True, "B": False, "C": True, "D": True}


def test_shown_again_at_old_place_and_saved(toolBar, buttonsSetting) -> None:
    menu = toolBar.buttonsMenu("Buttons", buttonsSetting)
    menuEntries(menu)["C"].setChecked(False)
    assert shown(toolBar) == ["A", "|", "D"]
    menuEntries(menu)["B"].setChecked(True)
    menuEntries(menu)["C"].setChecked(True)
    assert shown(toolBar) == ["A", "B", "|", "C", "D"]  # B before the separator
    menuEntries(menu)["D"].setChecked(False)
    assert sorted(buttonsSetting.value()) == ["D"]
    menuEntries(menu)["D"].setChecked(True)
    assert buttonsSetting.value() == []


def test_saved_choice_is_restored(toolBar, buttonsSetting) -> None:
    buttonsSetting.setValue(["A", "D"])
    toolBar.buttonsMenu("Buttons", buttonsSetting)
    assert shown(toolBar) == ["B", "|", "C"]


def test_icons_leave_room_in_bar(qapp) -> None:
    from aas_editor.settings.app_settings import TOOLBARS_HEIGHT
    from aas_editor.widgets.toolbar import ToolBar

    assert ToolBar(None).iconSize().height() < TOOLBARS_HEIGHT


def test_text_field_beside_bar_shrinks_first(qapp) -> None:
    from PyQt6.QtWidgets import QHBoxLayout, QLineEdit, QToolButton, QWidget

    from aas_editor.widgets.toolbar import ToolBar

    row = QWidget()
    layout = QHBoxLayout(row)
    bar = ToolBar(row)
    for name in "ABCDEFGHIJ":
        bar.addButton(QAction(name, bar), name)
    layout.addWidget(bar)
    layout.addWidget(QLineEdit())
    row.resize(bar.sizeHint().width() + 60, 30)
    row.show()
    qapp.processEvents()
    overflow = [b for b in bar.findChildren(QToolButton)
                if b.objectName() == "qt_toolbar_ext_button"]
    assert not any(b.isVisible() for b in overflow)
