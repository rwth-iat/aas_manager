#  Copyright (C) 2025  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
import logging
import os
import json
import shutil
import tempfile
import traceback
from typing import List

from jsonschema import validate, ValidationError

from PyQt6.QtWidgets import QDialog, QPushButton, QVBoxLayout, QFileDialog, QLineEdit, QComboBox, \
    QHBoxLayout, QLabel, QMessageBox, QListWidgetItem, QListWidget, QGroupBox, QFormLayout, QWidget, QCheckBox
from PyQt6.QtCore import pyqtSignal, QThread, QUrl
from PyQt6.QtGui import QIntValidator, QDesktopServices
from basyx.aas.adapter.json import AASToJsonEncoder, AASFromJsonDecoder

from basyx.aas.model import Submodel

from langchain_core.documents import Document

from aas_editor.widgets import messsageBoxes
from aas_editor.tools.handover_doc_llm.documentation_generator import json2document, documents2handover_documentation
from aas_editor.settings.icons import INFO_ICON

from aas_editor.tools.handover_doc_llm.config import PROMPT, LLM_PROVIDERS, TOOL_DESCRIPTION, RESPONSE_SCHEMA
from aas_editor.widgets.dropfilebox import DropFileQWebEngineView
from aas_editor.widgets.jsonEditor import JSONEditor

from langchain_community.document_loaders import PyPDFLoader
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

DOCUMENT_ROLE = 1000
# Keeps "all pages" of a long manual within context windows and provider rate limits
MAX_CONTEXT_CHARS = 60_000


def limit_context(docs: List[Document], max_chars: int) -> List[Document]:
    """Keep pages in order until max_chars, cutting the last kept page."""
    limited, total = [], 0
    for doc in docs:
        if total + len(doc.page_content) > max_chars:
            limited.append(Document(page_content=doc.page_content[:max_chars - total], metadata=doc.metadata))
            logging.warning(f"PDF text cut to the context limit: {max_chars} characters")
            break
        limited.append(doc)
        total += len(doc.page_content)
    return limited


def select_pages(docs: List[Document], pages_front: str, pages_end: str) -> List[Document]:
    """Keep the first pages_front and last pages_end pages (default 3 each, front -1 = all)."""
    front = int(pages_front) if pages_front.isdigit() or pages_front == "-1" else 3
    end = int(pages_end) if pages_end.isdigit() else 3
    if front != -1 and front + end < len(docs):
        # not docs[-end:]: for end == 0 that is the whole document
        return docs[:front] + docs[len(docs) - end:]
    return docs


class PdfProcessingThread(QThread):
    processing_complete = pyqtSignal(str)
    processing_error = pyqtSignal(str)
    show_answer_dialog = pyqtSignal(str)

    def __init__(self, file_path: str, llm_provider: str, llm_model: str, api_key: str,
                 pages_front: str, pages_end: str):
        super().__init__()
        self.file_path = file_path
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.api_key = api_key
        self.pages_front = pages_front
        self.pages_end = pages_end

    def init_llm(self, provider: str, chat_model: str, api_key: str, schema: dict = None):
        if provider in LLM_PROVIDERS:
            if provider == "Ollama" and schema is not None:
                return LLM_PROVIDERS[provider]["init"](chat_model, api_key, schema=schema)
            return LLM_PROVIDERS[provider]["init"](chat_model, api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def _fix_json_with_llm(self, llm, raw_answer: str, schema: dict, error_msg: str) -> str:
        from langchain_core.prompts import ChatPromptTemplate
        fix_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a JSON correction assistant. "
             "Return ONLY a valid JSON object. "
             "Do not include markdown, code fences, comments, or any extra text. "
             "The JSON MUST validate against the provided JSON Schema."),
            ("human",
             "JSON Schema:\n{schema}\n\n"
             "Validation / parsing error:\n{error}\n\n"
             "Original model output:\n{raw}\n\n"
             "Task: Produce corrected JSON that matches the schema exactly.")
        ])

        fix_chain = fix_prompt | llm
        fixed = fix_chain.invoke({"schema": json.dumps(schema), "error": error_msg, "raw": raw_answer})

        fixed_text = fixed.content if hasattr(fixed, "content") else str(fixed)
        return fixed_text.strip()

    def run(self):
        tmp_path = None
        try:
            # 1. Load the PDF pages from a temp copy of the file
            suffix = ".pdf"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_pdf:
                tmp_path = tmp_pdf.name
            shutil.copy2(self.file_path, tmp_path)

            loader = PyPDFLoader(tmp_path)
            docs = loader.load()

            # 2. Page Selection Logic
            docs = select_pages(docs, self.pages_front, self.pages_end)

            # 3. Cap the text
            docs = limit_context(docs, MAX_CONTEXT_CHARS)

            # 4. Chain Execution
            schema = json.loads(RESPONSE_SCHEMA)
            llm = self.init_llm(self.llm_provider, self.llm_model, self.api_key, schema=schema)
            prompt = ChatPromptTemplate.from_template(PROMPT)
            document_chain = create_stuff_documents_chain(llm, prompt)

            llm_response = document_chain.invoke({"input": "", "context": docs})
            answer = llm_response if isinstance(llm_response, str) else llm_response.get('answer', '')

            # 5. JSON Validation
            max_fix_attempts = 2
            last_error = None

            for attempt in range(max_fix_attempts + 1):
                try:
                    start_idx = answer.find("{")
                    end_idx = answer.rfind("}") + 1
                    if start_idx == -1 or end_idx == 0:
                        raise ValueError("No JSON found in response")

                    json_str = answer[start_idx:end_idx]
                    data = json.loads(json_str)
                    validate(instance=data, schema=schema)
                    self.show_answer_dialog.emit(json_str)
                    return

                except (ValueError, json.JSONDecodeError, ValidationError) as e:
                    last_error = str(e)

                    if attempt >= max_fix_attempts:
                        break

                    answer = self._fix_json_with_llm(
                        llm=llm,
                        raw_answer=answer,
                        schema=schema,
                        error_msg=last_error
                    )

            self.processing_error.emit(f"LLM response is not valid. Last error: {last_error}")

        except Exception:
            self.processing_error.emit(f"Error: {traceback.format_exc()}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)


class AnswerDialog(QDialog):
    VDI2770_CLASSIFICATION_SYSTEM = """// VDI2770 Classification System: 
// ID - Document class name
// "01-01" - Identification
// "02-01" - Technical specification
// "02-02" - Drawings, plans
// "02-03" - Assemblies
// "02-04" - Certificates, declarations
// "03-01" - Commissioning, de-commissioning
// "03-02" - Operation
// "03-03" - General safety
// "03-04" - Inspection, maintenance, testing
// "03-05" - Repair
// "03-06" - Spare parts
// "04-01" - Contract documents

"""


    def __init__(self, answer, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit LLM Extracted Answer")
        self.setMinimumSize(600, 400)
        layout = QVBoxLayout(self)
        self.text = JSONEditor(self)
        self.text.setText(self.VDI2770_CLASSIFICATION_SYSTEM + answer)
        layout.addWidget(self.text)
        ok_button = QPushButton("OK", self)
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)


class HandoverDocumentationToolDialog(QDialog):
    handoverExtracted = pyqtSignal(Submodel)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Handover Documentation Extractor")
        self.setMinimumSize(600, 700)

        self.documentListLabel = QLabel("Processed Documents:", self)
        self.documentListLabel.setFixedHeight(20)
        self.documentList = QListWidget(self)
        self.documentList.setMaximumHeight(150)
        self.documentList.setMinimumHeight(50)
        self.documentList.setToolTip("List of processed documents")


        self.html_renderer = DropFileQWebEngineView(self, emptyViewMsg="Drop PDF file here",
                             description="Drop a PDF file to extract Handover Documentation (VDI 2770).")
        self.html_renderer.fileDropped.connect(self.processPdf)
        self.html_renderer.setMinimumHeight(200)

        self.apiKeyLineEdit = QLineEdit(self, toolTip="API Key for LLM service",
                                        placeholderText="Enter API Key here",
                                        echoMode=QLineEdit.EchoMode.Password)
        self.apiKeyLabel = QLabel("API Key:", self)
        self.modelLineEdit = QLineEdit(self, toolTip="Choose model to use")
        self.providerLineEdit = QComboBox(self, toolTip="LLM Provider",
                                          currentIndexChanged=self.provider_changed)
        self.providerLineEdit.addItems([k for k in LLM_PROVIDERS.keys()])

        self.model_info_label = QLabel(self)
        self.model_info_label.setPixmap(INFO_ICON.pixmap(24, 24))
        self.model_info_label.setFixedSize(24, 24)
        self.model_info_label.setToolTip(
            "A custom model can be used, else the default model is being used.\nFor more information about models see \"https://docs.langchain.com/oss/python/integrations/chat\"")

        self.idLineEdit = QLineEdit(self, toolTip="ID of the generated Handover Documentation Submodel (mandatory)",
                                    placeholderText="Enter Submodel ID")
        self.idLineEdit.textChanged.connect(lambda txt: self.finishButton.setEnabled(bool(txt.strip())))

        self.chooseButton = QPushButton("Choose && Process PDF", self,
                                        toolTip="The selected PDF file will be processed and the extracted Handover Documentation will be shown.",
                                        clicked=self.chooseAndProcessPdf)

        self.pagesFrontLineEdit = QLineEdit(self,
                                            toolTip="Number of pages to use from the front of the document",
                                            placeholderText="default: 3; all pages = -1")
        self.pagesFrontLineEdit.setValidator(QIntValidator())
        self.pagesEndLineEdit = QLineEdit(self, toolTip="Number of pages to use from the end of the document",
                                          placeholderText="default: 3")
        self.pagesEndLineEdit.setValidator(QIntValidator())

        # Add option box widget to choose if to open PDF automatically when processing is done
        self.openPdfCheckbox = QCheckBox("Open Document when processing is done", self)
        self.openPdfCheckbox.setChecked(True)
        self.openPdfCheckbox.setToolTip("If checked, the document will be opened with the system default viewer "
                                        "after processing.")

        self.processingThread = None

        self.finishButton = QPushButton("Finish handover documentation", self)
        self.finishButton.setToolTip("Generate the handover documentation from the extracted documents.")
        self.finishButton.setEnabled(False)
        self.finishButton.clicked.connect(self.finish_handover_documentation)

        self._initLayout()

    @property
    def documents(self):
        document_items = [self.documentList.item(i) for i in range(self.documentList.count())]
        return [item.data(DOCUMENT_ROLE) for item in document_items]

    def _initLayout(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(TOOL_DESCRIPTION, self))

        # LLM settings group (provider, model, model-info, api key)
        gb_llm = QGroupBox("LLM Settings")
        llm_form = QFormLayout()

        llm_form.addRow(QLabel("AI Provider:"), self.providerLineEdit)

        model_container = QWidget()
        model_h = QHBoxLayout(model_container)
        model_h.setContentsMargins(0, 0, 0, 0)
        model_h.addWidget(self.modelLineEdit)
        model_h.addWidget(self.model_info_label)
        llm_form.addRow(QLabel("LLM Model:"), model_container)

        llm_form.addRow(self.apiKeyLabel, self.apiKeyLineEdit)
        gb_llm.setLayout(llm_form)
        layout.addWidget(gb_llm)

        # Pages selection group
        gb_pages = QGroupBox("Processing Settings")
        pages_layout = QFormLayout()
        pages_layout.addRow(QLabel("Front X pages to analyze:", self), self.pagesFrontLineEdit)
        pages_layout.addRow(QLabel("End Y pages to analyze:", self), self.pagesEndLineEdit)
        pages_layout.addWidget(self.openPdfCheckbox)
        gb_pages.setLayout(pages_layout)
        layout.addWidget(gb_pages)

        # Submodel group
        gb_id = QGroupBox("Handover Submodel")
        sm_form = QFormLayout()
        sm_form.addRow(QLabel("Submodel ID*:", self), self.idLineEdit)
        sm_form.addRow(self.documentListLabel, self.documentList)
        sm_form.addWidget(self.chooseButton)
        sm_form.addWidget(self.html_renderer)
        gb_id.setLayout(sm_form)

        layout.addWidget(gb_id)
        layout.addWidget(self.finishButton)
        self.setLayout(layout)

    def chooseAndProcessPdf(self):
        file, _ = QFileDialog.getOpenFileName(self, "Open PDF file", filter="PDF Files (*.pdf)")
        if file:
            self.processPdf(file)

    def processPdf(self, file: str):
        if self.processingThread:
            QMessageBox.information(self, "Processing", "A PDF is still being processed. Please wait until it is done.")
            return
        self.current_file = file
        self.current_filename = os.path.basename(self.current_file)
        self.html_renderer.setHtml("""
            <div style='text-align: center; padding: 50px; font-size: 18px;'>
                <div style='margin-bottom: 20px;'>Processing PDF...</div>
                <div class="spinner"></div>
            </div>
            <style>
                .spinner {
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #3498db;
                    border-radius: 50%;
                    width: 50px;
                    height: 50px;
                    animation: spin 1s linear infinite;
                    margin: 0 auto;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        """)

        model_text = self.modelLineEdit.text() if self.modelLineEdit.text() else self.modelLineEdit.placeholderText()
        self.processingThread = PdfProcessingThread(
            file,
            self.providerLineEdit.currentText(),
            model_text,
            self.apiKeyLineEdit.text(),
            pages_front=self.pagesFrontLineEdit.text(),
            pages_end=self.pagesEndLineEdit.text(),
        )

        self.processingThread.processing_error.connect(self.on_processing_error)
        self.processingThread.show_answer_dialog.connect(self.show_answer_dialog)

        self.chooseButton.setEnabled(False)
        self.processingThread.start()

    def cleanup_thread(self):
        if self.processingThread:
            self.processingThread.quit()
            self.processingThread.wait()
            self.processingThread.deleteLater()
            self.processingThread = None
            self.chooseButton.setEnabled(True)

    def on_processing_error(self, error_message):
        self.html_renderer.setHtml(f"<div style='color:red;'>{error_message}</div>")
        self.cleanup_thread()

    def provider_changed(self):
        provider = self.providerLineEdit.currentText()
        self.modelLineEdit.setPlaceholderText(LLM_PROVIDERS[provider]["default_model"])
        if provider == "Ollama":
            self.apiKeyLabel.setText("Base URL:")
            self.apiKeyLineEdit.setPlaceholderText("http://localhost:11434 (leave empty for default)")
            self.apiKeyLineEdit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.apiKeyLineEdit.setToolTip("Base URL of the Ollama server (leave empty for default)")
        else:
            self.apiKeyLabel.setText("API Key:")
            self.apiKeyLineEdit.setPlaceholderText("Enter API Key here")
            self.apiKeyLineEdit.setEchoMode(QLineEdit.EchoMode.Password)
            self.apiKeyLineEdit.setToolTip("API Key for LLM service")

    def closeEvent(self, event):
        if self.processingThread and self.processingThread.isRunning():
            self.processingThread.quit()
            self.processingThread.wait()
        super().closeEvent(event)

    def _update_document_list_height(self):
        count = self.documentList.count()
        item_height = self.documentList.sizeHintForRow(0) if count > 0 else 20
        new_height = min(150, item_height * count + 2 * self.documentList.frameWidth())
        self.documentList.setFixedHeight(new_height)

    def show_answer_dialog(self, answer):
        # Open the file with the default OS handler if user enabled it
        if self.openPdfCheckbox.isChecked():
            file_url = QUrl.fromLocalFile(os.path.abspath(self.current_file))
            if not QDesktopServices.openUrl(file_url):
                logging.warning(f"Could not open file: {self.current_file}")

        self.cleanup_thread()
        dialog = AnswerDialog(answer, self)

        while dialog.exec():
            try:
                json_str = dialog.text.text()
                document = json2document(json_str, self.current_filename)

                item = QListWidgetItem(self.current_filename)
                item.setData(DOCUMENT_ROLE, document)
                item.setToolTip(self.current_file)
                self.documentList.addItem(item)
                self._update_document_list_height()

                self.adjustSize()
                self.resize(max(self.width(), 600), max(self.height(), 650))

                self.html_renderer.setHtml("""
                    <div style="display:flex;flex-direction:column;justify-content:center;align-items:center;height:100%;">
                        <div style="width:50px;height:50px;margin-bottom:20px;"><svg xmlns="http://www.w3.org/2000/svg" id="mdi-open-in-app" viewBox="0 0 24 24"><path d="M12,10L8,14H11V20H13V14H16M19,4H5C3.89,4 3,4.9 3,6V18A2,2 0 0,0 5,20H9V18H5V8H19V18H15V20H19A2,2 0 0,0 21,18V6A2,2 0 0,0 19,4Z" /></svg></div>
                        <div style="text-align:center;">Drop another PDF file here</div>
                        <div style="text-align:center;">Drop a PDF file to extract Handover Documentation (VDI 2770).</div>
                    </div>
                    """)

                QMessageBox.information(self, "Extraction Successful", "Document extracted successfully!")
                return
            except Exception as e:
                messsageBoxes.ErrorMessageBox.withTraceback(self, str(e)).exec()
                continue
        dialog.deleteLater()

    def finish_handover_documentation(self):
        try:
            if not self.documents:
                messsageBoxes.ErrorMessageBox(self, "No documents extracted!").exec()
                return
            id_ = self.idLineEdit.text() if self.idLineEdit.text() else "None"
            handover_sm = documents2handover_documentation(self.documents, id_=id_)
            normalized_json = json.dumps(handover_sm, cls=AASToJsonEncoder)
            normalized_handover_sm = json.loads(normalized_json, cls=AASFromJsonDecoder)
        except Exception as e:
            messsageBoxes.ErrorMessageBox.withTraceback(self, str(e)).exec()
            return


        self.handoverExtracted.emit(normalized_handover_sm)
        self.accept()
