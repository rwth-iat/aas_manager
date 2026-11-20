# QtWebEngineWidgets must be imported before the QApplication exists (qapp)
from PyQt6 import QtWebEngineWidgets  # noqa: F401


def test_path_field_gets_most_of_a_narrow_tab(qapp) -> None:
    from aas_editor.widgets.tab import TabWidget, TabWithTreeView

    tabs = TabWidget()
    tab = TabWithTreeView(parent=tabs)
    tabs.addTab(tab, "item")
    tabs.resize(550, 300)
    tabs.show()
    qapp.processEvents()
    # The path row holds only back/forward, path and type: path takes the rest
    rest = tab.width() - tab.pathToolBar.width() - tab.objTypeLine.width()
    assert tab.pathLine.width() >= rest - 20  # layout spacing
