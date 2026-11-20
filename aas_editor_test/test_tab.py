# QtWebEngineWidgets must be imported before the QApplication exists (qapp)
from PyQt6 import QtWebEngineWidgets  # noqa: F401
from PyQt6.QtCore import Qt


def test_path_field_gets_most_of_a_narrow_tab(qapp) -> None:
    from aas_editor.widgets.tab import TabWidget, TabWithTreeView

    tabs = TabWidget()
    tab = TabWithTreeView(parent=tabs)
    tabs.addTab(tab, "item")
    tabs.resize(550, 300)
    tabs.show()
    qapp.processEvents()
    # The path row holds only the path
    assert tab.pathBar.width() >= tab.width() - 10


def test_history_buttons_in_toolbar_and_path_at_bottom(qapp) -> None:
    from aas_editor.widgets.tab import TabWidget, TabWithTreeView

    tabs = TabWidget()
    tab = TabWithTreeView(parent=tabs)
    tabs.addTab(tab, "item")
    tabs.resize(550, 300)
    tabs.show()
    qapp.processEvents()
    assert tab.toolBar.actions()[:2] == [tab.backAct, tab.forwardAct]
    assert tab.pathBar.mapTo(tab, tab.pathBar.rect().topLeft()).y() > \
        tab.splitter.geometry().bottom()
    # Type field: top row, at the right border
    typeLine = tab.objTypeLine
    typeTopLeft = typeLine.mapTo(tab, typeLine.rect().topLeft())
    assert typeTopLeft.y() + typeLine.height() <= tab.splitter.geometry().top()
    assert typeTopLeft.x() + typeLine.width() >= tab.width() - 5


def pathModel():
    from PyQt6.QtGui import QIcon, QPixmap, QStandardItem, QStandardItemModel

    pixmap = QPixmap(16, 16)
    pixmap.fill()
    model = QStandardItemModel()
    parent = model.invisibleRootItem()
    for name in ["file.aasx", "Submodel", "Collection", "Property"]:
        # Like a real file node, the root has no icon
        item = QStandardItem(name) if parent is model.invisibleRootItem() \
            else QStandardItem(QIcon(pixmap), name)
        parent.appendRow(item)
        parent = item
    return model, parent.index()


def test_path_bar_shows_one_segment_per_level(qapp) -> None:
    from aas_editor.widgets.tab import PathBar

    model, leaf = pathModel()
    bar = PathBar()
    bar.setIndex(leaf)
    assert [b.text() for b in bar.segments] == \
        ["file.aasx", "Submodel", "Collection", "Property"]
    bar.setIndex(leaf.parent())
    assert [b.text() for b in bar.segments] == ["file.aasx", "Submodel", "Collection"]


def test_click_on_segment_emits_its_item(qapp) -> None:
    from aas_editor.widgets.tab import PathBar

    model, leaf = pathModel()
    bar = PathBar()
    bar.setIndex(leaf)
    clicked = []
    bar.itemClicked.connect(clicked.append)
    bar.segments[1].click()
    assert clicked == [leaf.parent().parent()]


def test_narrow_path_bar_collapses_leading_segments_to_icons(qapp) -> None:
    from PyQt6.QtWidgets import QToolButton

    from aas_editor.widgets.tab import PathBar

    model, leaf = pathModel()
    bar = PathBar()
    bar.setIndex(leaf)
    bar.resize(bar.sizeHint().width() - 100, 30)
    bar.show()
    qapp.processEvents()
    styles = [b.toolButtonStyle() for b in bar.segments]
    assert bar.segments[0].text() == "…"  # no icon to show
    assert bar.segments[0].toolTip() == "file.aasx"
    assert styles[1] == Qt.ToolButtonStyle.ToolButtonIconOnly
    assert styles[-1] == Qt.ToolButtonStyle.ToolButtonTextBesideIcon
    bar.resize(bar.sizeHint().width() + 500, 30)
    qapp.processEvents()
    assert all(b.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonTextBesideIcon
               for b in bar.segments)
    assert bar.segments[0].text() == "file.aasx"


def test_too_narrow_path_bar_elides_last_name(qapp) -> None:
    from aas_editor.widgets.tab import PathBar

    model, leaf = pathModel()
    bar = PathBar()
    bar.setIndex(leaf)
    bar.resize(170, 30)  # all leading segments collapsed: 190 px
    bar.show()
    qapp.processEvents()
    last = bar.segments[-1]
    assert last.text().endswith("…") and last.text() != "…"
    assert bar.layout().sizeHint().width() <= bar.width()


def test_path_bar_skips_group_nodes_like_submodels(qapp) -> None:
    from basyx.aas import model as aas
    from PyQt6.QtGui import QStandardItem, QStandardItemModel

    from aas_editor.settings import OBJECT_ROLE
    from aas_editor.widgets.tab import PathBar

    model = QStandardItemModel()
    operation = QStandardItem("op")
    operation.setData(aas.Operation(id_short="op"), OBJECT_ROLE)
    group = QStandardItem("input_variable")  # pack view attr of Operation
    prop = QStandardItem("Prop")
    model.appendRow(operation)
    operation.appendRow(group)
    group.appendRow(prop)
    bar = PathBar()
    bar.setIndex(prop.index())
    assert [b.text() for b in bar.segments] == ["op", "Prop"]
    bar.setIndex(group.index())  # the open item itself is always shown
    assert [b.text() for b in bar.segments] == ["op", "input_variable"]
