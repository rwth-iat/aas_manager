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
