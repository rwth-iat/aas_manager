from pathlib import Path
from types import SimpleNamespace

# QtWebEngineWidgets must be imported before the QApplication exists (qapp fixture)
from PyQt6 import QtWebEngineWidgets  # noqa: F401
from basyx.aas.model import Submodel


class TestScanSubmodelTemplates:
    def test_template_in_two_formats_is_loaded_once(self, qapp: object, tmp_path: Path, monkeypatch) -> None:
        from aas_editor.package import Package
        from aas_editor.treeviews.treeview_pack import PackTreeView

        pkg = Package()
        pkg.add(Submodel("urn:sm1"))
        pkg.write(tmp_path / "a.json")
        pkg.write(tmp_path / "a.aasx")
        monkeypatch.setattr("aas_editor.treeviews.treeview_pack.SUBMODEL_TEMPLATES_FOLDER", tmp_path)
        probe = SimpleNamespace(copyBufferObjStores={})

        PackTreeView.scanFolderForExistFiles(probe)

        assert list(probe.copyBufferObjStores) == [Path("a.json")]
