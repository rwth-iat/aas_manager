import warnings
from pathlib import Path

from PyQt6.QtCore import qInstallMessageHandler
from PyQt6.QtWidgets import QTreeView, QWidget

import aas_editor
from aas_editor.widgets.search import SearchBar  # before QApplication: WebEngine


def testPackageCompilesWithoutSyntaxWarning() -> None:
    for path in Path(aas_editor.__file__).parent.rglob("*.py"):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            compile(path.read_text(), str(path), "exec")


def testSearchBarSetsNoSecondLayout(qapp) -> None:
    messages: list[str] = []
    previous = qInstallMessageHandler(lambda mode, ctx, msg: messages.append(msg))
    try:
        parent = QWidget()
        view = QTreeView(parent)
        view.modelChanged = view.windowTitleChanged  # SearchBar connects to it
        SearchBar(view, filterColumns=[0], parent=parent)
    finally:
        qInstallMessageHandler(previous)
    assert not [m for m in messages if "already has a layout" in m]
