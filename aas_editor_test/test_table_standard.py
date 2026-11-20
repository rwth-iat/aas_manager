# QtWebEngineWidgets must be imported before the QApplication exists (qapp fixture)
from PyQt6 import QtWebEngineWidgets  # noqa: F401
from PyQt6.QtCore import QModelIndex


class TestUndoLimit:
    def test_reset_keeps_undo_limit(self, qapp: object) -> None:
        from aas_editor.models import StandardTable
        from aas_editor.settings.app_settings import MAX_UNDOS, UNDO_ROLE

        model = StandardTable()
        model.setData(QModelIndex(), [], UNDO_ROLE)
        for i in range(MAX_UNDOS + 5):
            model.undo.append(i)

        assert model.undo.maxlen == MAX_UNDOS
        assert len(model.undo) == MAX_UNDOS


def newItems(count: int):
    from aas_editor.models import StandardItem

    root = StandardItem([], "root")
    children = [StandardItem(i, f"c{i}", parent=root) for i in range(count)]
    return root, children


class TestChildCache:
    def test_children_cached_until_change(self, qapp: object) -> None:
        root, children = newItems(3)
        assert root.children() is root.children()
        assert list(root.children()) == children

    def test_added_child_is_listed_with_its_row(self, qapp: object) -> None:
        from aas_editor.models import StandardItem

        root, children = newItems(3)
        root.children()  # fill the cache first
        added = StandardItem(3, "c3", parent=root)
        assert list(root.children()) == children + [added]
        assert added.row() == 3

    def test_removed_child_shifts_rows(self, qapp: object) -> None:
        root, children = newItems(3)
        assert children[2].row() == 2
        children[0].setParent(None)
        assert list(root.children()) == children[1:]
        assert children[2].row() == 1

    def test_model_parent_row_in_wide_node(self, qapp: object) -> None:
        from aas_editor.models import StandardItem, StandardTable

        root, children = newItems(500)
        grandChild = StandardItem(0, "g", parent=children[300])
        model = StandardTable(rootItem=root)
        child = model.index(0, 0, model.index(300, 0))
        assert model.objByIndex(child) is grandChild
        assert model.parent(child).row() == 300


class TestPackageAttrsReadOnly:
    def test_package_attributes_are_not_editable(self, qapp: object, aasx_file) -> None:
        from PyQt6.QtCore import Qt
        from aas_editor.models import DetailedInfoTable
        from aas_editor.package import Package
        from aas_editor.settings.app_settings import NAME_ROLE, VALUE_COLUMN
        from aas_editor_test.test_performance import newPackTreeView

        view = newPackTreeView()
        view.add_pack_to_tree(Package(aasx_file))
        detailed = DetailedInfoTable(view.sourceModel().index(0, 0))
        names = []
        for row in range(detailed.rowCount()):
            index = detailed.index(row, VALUE_COLUMN)
            names.append(index.data(NAME_ROLE))
            assert not index.flags() & Qt.ItemFlag.ItemIsEditable, names[-1]
        assert {"file", "objStore", "files", "writeJsonInAasx"} <= set(names)


class TestInsertAt:
    def test_list(self, qapp: object) -> None:
        from aas_editor.models.table_standard import insertAt

        items = ["a", "c"]
        insertAt(items, "b", 1)
        insertAt(items, "d", None)
        assert items == ["a", "b", "c", "d"]

    def test_namespace_set_keeps_order_and_parent(self, qapp: object) -> None:
        from basyx.aas import model
        from aas_editor.models.table_standard import insertAt

        submodel = model.Submodel("urn:sm", submodel_element=[
            model.Property(name, model.datatypes.String) for name in ("a", "c")])
        b = model.Property("b", model.datatypes.String)
        insertAt(submodel.submodel_element, b, 1)
        assert [e.id_short for e in submodel.submodel_element] == ["a", "b", "c"]
        assert all(e.parent is submodel for e in submodel.submodel_element)

    def test_dict(self, qapp: object) -> None:
        from aas_editor.additional.classes import DictItem
        from aas_editor.models.table_standard import insertAt

        items = {"a": 1, "c": 3}
        insertAt(items, DictItem("b", 2), 1)
        assert list(items.items()) == [("a", 1), ("b", 2), ("c", 3)]
