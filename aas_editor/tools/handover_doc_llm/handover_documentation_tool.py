#  Copyright (C) 2025  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/

import os
import json
import tempfile
import traceback

from PyQt6.QtWidgets import QDialog, QPushButton, QVBoxLayout, QFileDialog, QLineEdit, QComboBox, \
    QHBoxLayout, QTextEdit, QLabel
from PyQt6.QtCore import pyqtSignal, QThread
from PyQt6.QtGui import QIntValidator

from basyx.aas.model import Submodel

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from tools.handover_doc_llm.documentation_generator import json2handover_documentation
from aas_editor.settings.icons import INFO_ICON

from tools.handover_doc_llm.config import PROMPT, LLM_PROVIDERS, EMBEDDING_PROVIDERS
from aas_editor.widgets.dropfilebox import DropFileQWebEngineView


class PdfProcessingThread(QThread):
    processing_complete = pyqtSignal(str)
    processing_error = pyqtSignal(str)
    show_answer_dialog = pyqtSignal(str)

    def __init__(self, file_path, provider_text, model_text, api_key, pages_front, pages_end):
        super().__init__()
        self.file_path = file_path
        self.provider_text = provider_text
        self.model_text = model_text
        self.api_key = api_key
        self.pages_front = pages_front
        self.pages_end = pages_end

    def init_embeddings(self, provider: str = "default", api_key: str = None):
        if provider in EMBEDDING_PROVIDERS:
            return EMBEDDING_PROVIDERS[provider](api_key)
        else:
            return EMBEDDING_PROVIDERS["default"](api_key)

    def init_llm(self, provider: str, chat_model: str, api_key: str):
        if provider in LLM_PROVIDERS:
            return LLM_PROVIDERS[provider]["init"](chat_model, api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def run(self):
        try:
            tmp_path = None

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                tmp_pdf.write(open(self.file_path, "rb").read())
                tmp_path = tmp_pdf.name

            loader = PyPDFLoader(tmp_path)
            docs = loader.load()
            if self.pages_front.isdigit():
                docs = docs[:int(self.pages_front)]
            if self.pages_end.isdigit() and int(self.pages_end) + int(self.pages_front) < len(docs):
                docs = docs[-int(self.pages_end):]

            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            splits = splitter.split_documents(docs)

            embeddings = self.init_embeddings(self.provider_text, self.api_key)
            vector_store = FAISS.from_documents(splits, embeddings)
            retriever = vector_store.as_retriever()

            llm = self.init_llm(self.provider_text, self.model_text, self.api_key)
            prompt = ChatPromptTemplate.from_template(PROMPT)

            rag_chain = create_retrieval_chain(retriever, create_stuff_documents_chain(llm, prompt))
            llm_response = rag_chain.invoke({"input": ""})

            llm_response = llm_response['answer']

            try:
                json_str = llm_response[llm_response.find("{"):llm_response.rfind("}") + 1]
                json.loads(json_str, strict=True)
            except json.JSONDecodeError as e:
                return self.processing_error.emit(f"Error, LLM Response not well formatted! {e}")

            self.show_answer_dialog.emit(json_str)

        except Exception:
            err_msg = traceback.format_exc()
            self.processing_error.emit(f"Error: {err_msg}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)


class AnswerDialog(QDialog):
    def __init__(self, answer, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LLM Extracted Answer")
        self.setMinimumSize(600, 400)
        layout = QVBoxLayout(self)
        text = QTextEdit(self)
        text.setText(answer)
        layout.addWidget(text)
        ok_button = QPushButton("OK", self)
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)


class HandoverDocumentationToolDialog(QDialog):
    handoverExtracted = pyqtSignal(Submodel)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._initLayout()
        self.setWindowTitle("Handover Documentation Extractor")
        self.setMinimumSize(600, 400)

        description = "Drop a PDF file to extract Handover Documentation (VDI 2770)."
        self.html_renderer = DropFileQWebEngineView(self, emptyViewMsg="Drop PDF file here", description=description)
        self.html_renderer.fileDropped.connect(self.processPdf)

        self.apiKey = QLineEdit(self, toolTip="API Key for LLM service", placeholderText="Enter API Key here",
                                echoMode=QLineEdit.EchoMode.Password)
        self.model = QLineEdit(self, toolTip="Choose model to use")
        self.provider = QComboBox(self, toolTip="LLM Provider",
                                  currentIndexChanged=self.provider_changed)
        self.provider.addItems([k for k in LLM_PROVIDERS.keys()])

        self.model_info_label = QLabel(self)
        self.model_info_label.setPixmap(INFO_ICON.pixmap(24, 24))
        self.model_info_label.setFixedSize(24, 24)
        self.model_info_label.setToolTip(
            "A custom model can be used, else the default model is being used.\nFor more information about models see \"https://js.langchain.com/docs/integrations/chat/\"")

        self.chooseButton = QPushButton("Choose && Process PDF", self,
                                        toolTip="The selected PDF file will be processed and the extracted Handover Documentation will be shown.",
                                        clicked=self.chooseAndProcessPdf)

        self.pages_front = QLineEdit(self,
                                     toolTip="Number of pages to use from the front of the document (empty = all)",
                                     placeholderText="Front X pages")
        self.pages_front.setValidator(QIntValidator())
        self.pages_end = QLineEdit(self, toolTip="Number of pages to use from the end of the document (empty = all)",
                                   placeholderText="End X pages")
        self.pages_end.setValidator(QIntValidator())

        self.layout().addWidget(self.html_renderer)

        layout_pages = QHBoxLayout()
        layout_pages.addWidget(self.pages_front)
        layout_pages.addWidget(self.pages_end)
        self.layout().addLayout(layout_pages)

        layout_model = QHBoxLayout()
        layout_model.addWidget(self.provider)
        layout_model.addWidget(self.model)
        layout_model.addWidget(self.model_info_label)
        self.layout().addLayout(layout_model)

        self.layout().addWidget(self.apiKey)
        self.layout().addWidget(self.chooseButton)
        self.layout().addWidget(self.apiKey)
        self.layout().addWidget(self.chooseButton)

        self.processing_thread = None

    def _initLayout(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)

    def chooseAndProcessPdf(self):
        file, _ = QFileDialog.getOpenFileName(self, "Open PDF file", filter="PDF Files (*.pdf)")
        if file:
            self.processPdf(file)

    def processPdf(self, file: str):
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

        model_text = self.model.text() if self.model.text() else self.model.placeholderText()
        self.processing_thread = PdfProcessingThread(
            file,
            self.provider.currentText(),
            model_text,
            self.apiKey.text(),
            pages_front=self.pages_front.text(),
            pages_end=self.pages_end.text(),
        )

        self.processing_thread.processing_error.connect(self.on_processing_error)
        self.processing_thread.show_answer_dialog.connect(self.show_answer_dialog)

        self.processing_thread.start()

    def cleanup_thread(self):
        if self.processing_thread:
            self.processing_thread.quit()
            self.processing_thread.wait()
            self.processing_thread.deleteLater()
            self.processing_thread = None

    def on_processing_error(self, error_message):
        self.html_renderer.setHtml(f"<div style='color:red;'>{error_message}</div>")
        self.cleanup_thread()

    def provider_changed(self):
        self.model.setPlaceholderText(LLM_PROVIDERS[self.provider.currentText()]["default_model"])

    def closeEvent(self, event):
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.quit()
            self.processing_thread.wait()
        super().closeEvent(event)

    def show_answer_dialog(self, answer):
        self.cleanup_thread()
        dialog = AnswerDialog(answer, self)
        if dialog.exec():
            json_str = dialog.findChild(QTextEdit).toPlainText()
            try:
                handover = json2handover_documentation(json_str)
                self.accept()
                self.handoverExtracted.emit(handover)
            except Exception:
                err_msg = traceback.format_exc()
                self.html_renderer.setHtml(f"<div style='color:red;'>{err_msg}</div>")
