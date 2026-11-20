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
