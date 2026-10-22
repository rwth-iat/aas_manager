import json
from pathlib import Path
from types import SimpleNamespace

# QtWebEngineWidgets must be imported before the QApplication exists (qapp fixture)
from PyQt6 import QtWebEngineWidgets  # noqa: F401
from basyx.aas.adapter.json import AASToJsonEncoder

TITLE = 'Betriebsanleitung für "XYZ"'
DESCRIPTION = "Zeile 1\nZeile 2"


def _strings(node):
    if isinstance(node, dict):
        for value in node.values():
            yield from _strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _strings(value)
    elif isinstance(node, str):
        yield node


class TestFinishHandoverDocumentation:
    def test_text_survives_round_trip(self, qapp: object, tmp_path: Path, monkeypatch) -> None:
        from aas_editor.tools.handover_doc_llm.documentation_generator import json2document
        from aas_editor.tools.handover_doc_llm.handover_documentation_tool import HandoverDocumentationToolDialog

        monkeypatch.chdir(tmp_path)
        answer = json.dumps({"document": {
            "documentId": {"documentDomainId": "example", "documentIdentifier": "222-101"},
            "documentClassification": {"classId": "03-02"},
            "documentVersion": {"title": {"de": TITLE}, "description": {"de": DESCRIPTION},
                                "keyWords": {"de": "Handbuch"}, "language": ["de"], "version": "1"},
        }})
        emitted = []
        dialog = SimpleNamespace(
            documents=[json2document(answer, "manual.pdf")],
            idLineEdit=SimpleNamespace(text=lambda: "urn:handover"),
            handoverExtracted=SimpleNamespace(emit=emitted.append),
            accept=lambda: None,
        )

        HandoverDocumentationToolDialog.finish_handover_documentation(dialog)

        texts = set(_strings(json.loads(json.dumps(emitted[0], cls=AASToJsonEncoder))))
        assert TITLE in texts
        assert DESCRIPTION in texts
        assert not (tmp_path / "handover_sm.json").exists()


class TestLimitContext:
    def test_pages_cut_at_cap_in_order(self, qapp: object) -> None:
        from langchain_core.documents import Document
        from aas_editor.tools.handover_doc_llm.handover_documentation_tool import limit_context

        pages = [Document(page_content=text) for text in ("aaaa", "bbbb", "cccc")]

        assert limit_context(pages, 100) == pages
        limited = limit_context(pages, 6)
        assert [page.page_content for page in limited] == ["aaaa", "bb"]
