import json
from pathlib import Path
from types import SimpleNamespace

import pytest

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


class TestProcessPdf:
    def test_second_pdf_is_refused_while_processing(self, qapp: object, monkeypatch) -> None:
        from PyQt6.QtWidgets import QMessageBox
        from aas_editor.tools.handover_doc_llm import handover_documentation_tool as tool

        monkeypatch.setattr(tool.PdfProcessingThread, "start", lambda self: None)
        boxes = []
        monkeypatch.setattr(QMessageBox, "information", lambda parent, title, text: boxes.append(title))
        dialog = tool.HandoverDocumentationToolDialog()

        dialog.processPdf("a.pdf")
        dialog.processPdf("b.pdf")

        assert dialog.current_file == "a.pdf"
        assert boxes == ["Processing"]
        assert not dialog.chooseButton.isEnabled()
        dialog.cleanup_thread()
        assert dialog.chooseButton.isEnabled()


class TestLimitContext:
    def test_pages_cut_at_cap_in_order(self, qapp: object) -> None:
        from langchain_core.documents import Document
        from aas_editor.tools.handover_doc_llm.handover_documentation_tool import limit_context

        pages = [Document(page_content=text) for text in ("aaaa", "bbbb", "cccc")]

        assert limit_context(pages, 100) == pages
        limited = limit_context(pages, 6)
        assert [page.page_content for page in limited] == ["aaaa", "bb"]


class TestJson2Document:
    def test_invalid_json_raises(self, qapp: object) -> None:
        from aas_editor.tools.handover_doc_llm.documentation_generator import json2document

        with pytest.raises(json.JSONDecodeError):
            json2document('{"document": {,}}', "x.pdf")


class TestEncryptedPdf:
    def test_encrypted_pdf_text_is_read(self, qapp: object, tmp_path: Path) -> None:
        from langchain_community.document_loaders import PyPDFLoader
        from pypdf import PdfWriter
        from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

        writer = PdfWriter()
        page = writer.add_blank_page(width=612, height=792)
        font = DictionaryObject({NameObject("/Type"): NameObject("/Font"),
                                 NameObject("/Subtype"): NameObject("/Type1"),
                                 NameObject("/BaseFont"): NameObject("/Helvetica")})
        page[NameObject("/Resources")] = DictionaryObject(
            {NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})})
        content = DecodedStreamObject()
        content.set_data(b"BT /F1 12 Tf 72 712 Td (Encrypted hello) Tj ET")
        page[NameObject("/Contents")] = writer._add_object(content)
        # Owner password only, like manufacturer datasheets: opens without a password
        writer.encrypt(user_password="", owner_password="owner", algorithm="AES-128")
        pdf = tmp_path / "encrypted.pdf"
        writer.write(pdf)

        docs = PyPDFLoader(str(pdf)).load()

        assert "Encrypted hello" in docs[0].page_content
