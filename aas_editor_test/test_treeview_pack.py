from pathlib import Path
from types import SimpleNamespace

# QtWebEngineWidgets must be imported before the QApplication exists (qapp fixture)
from PyQt6 import QtWebEngineWidgets  # noqa: F401
from basyx.aas.model import Submodel


def writeTemplate(folder: Path, *names: str) -> None:
    from aas_editor.package import Package

    pkg = Package()
    pkg.add(Submodel("urn:sm1", id_short="sm1"))
    for name in names:
        pkg.write(folder / name)


class TestScanSubmodelTemplates:
    def test_template_in_two_formats_is_listed_once(self, qapp: object, tmp_path: Path, monkeypatch) -> None:
        from aas_editor.treeviews.treeview_pack import PackTreeView

        writeTemplate(tmp_path, "a.json", "a.aasx")
        monkeypatch.setattr("aas_editor.treeviews.treeview_pack.SUBMODEL_TEMPLATES_FOLDER", tmp_path)
        probe = SimpleNamespace()

        PackTreeView.scanFolderForExistFiles(probe)

        assert probe.templateFiles == [Path("a.json")]

    def test_scan_does_not_parse_templates(self, qapp: object, tmp_path: Path, monkeypatch) -> None:
        from aas_editor.treeviews.treeview_pack import PackTreeView

        (tmp_path / "broken.json").write_text("not json")
        monkeypatch.setattr("aas_editor.treeviews.treeview_pack.SUBMODEL_TEMPLATES_FOLDER", tmp_path)
        monkeypatch.setattr("aas_editor.treeviews.treeview_pack.read_aas_json_file",
                            lambda *a: (_ for _ in ()).throw(AssertionError("parsed at scan")))
        probe = SimpleNamespace()

        PackTreeView.scanFolderForExistFiles(probe)

        assert probe.templateFiles == [Path("broken.json")]


class TestOnTemplateFileChosen:
    def test_chosen_submodel_is_pasted(self, qapp: object, tmp_path: Path, monkeypatch) -> None:
        from aas_editor.treeviews.treeview_pack import PackTreeView

        writeTemplate(tmp_path, "a.json")
        monkeypatch.setattr("aas_editor.treeviews.treeview_pack.SUBMODEL_TEMPLATES_FOLDER", tmp_path)
        shown = []
        monkeypatch.setattr("aas_editor.treeviews.treeview_pack.QInputDialog.getItem",
                            lambda parent, title, label, items, current, editable: (shown.extend(items) or items[0], True))
        pasted = []
        probe = SimpleNamespace(pasteSubmodel=pasted.append)

        PackTreeView.onTemplateFileChosen(probe, Path("a.json"))

        assert shown == ["sm1 (urn:sm1)"]
        assert [sm.id for sm in pasted] == ["urn:sm1"]

    def test_cancel_pastes_nothing(self, qapp: object, tmp_path: Path, monkeypatch) -> None:
        from aas_editor.treeviews.treeview_pack import PackTreeView

        writeTemplate(tmp_path, "a.json")
        monkeypatch.setattr("aas_editor.treeviews.treeview_pack.SUBMODEL_TEMPLATES_FOLDER", tmp_path)
        monkeypatch.setattr("aas_editor.treeviews.treeview_pack.QInputDialog.getItem",
                            lambda *a: ("", False))
        pasted = []
        probe = SimpleNamespace(pasteSubmodel=pasted.append)

        PackTreeView.onTemplateFileChosen(probe, Path("a.json"))

        assert pasted == []


class TestReadTemplateSubmodels:
    def test_returns_submodels_of_file(self, qapp: object, tmp_path: Path) -> None:
        from aas_editor.treeviews.treeview_pack import readTemplateSubmodels

        writeTemplate(tmp_path, "a.aasx")

        submodels = readTemplateSubmodels(tmp_path / "a.aasx")

        assert [sm.id for sm in submodels] == ["urn:sm1"]

    def test_broken_file_gives_no_submodels(self, qapp: object, tmp_path: Path) -> None:
        from aas_editor.treeviews.treeview_pack import readTemplateSubmodels

        (tmp_path / "broken.json").write_text("not json")

        assert readTemplateSubmodels(tmp_path / "broken.json") == []
