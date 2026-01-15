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
import tempfile
import traceback

from PyQt6.QtWidgets import QDialog, QPushButton, QVBoxLayout, QFileDialog, QLineEdit, QComboBox, \
    QHBoxLayout, QLabel, QMessageBox, QListWidgetItem, QListWidget
from PyQt6.QtCore import pyqtSignal, QThread, QUrl
from PyQt6.QtGui import QIntValidator, QDesktopServices
from basyx.aas.adapter.json import AASToJsonEncoder, AASFromJsonDecoder

from basyx.aas.model import Submodel

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from widgets import messsageBoxes
from tools.handover_doc_llm.documentation_generator import json2document, documents2handover_documentation
from aas_editor.settings.icons import INFO_ICON

from tools.handover_doc_llm.config import PROMPT, LLM_PROVIDERS, EMBEDDING_PROVIDERS, TOOL_DESCRIPTION
from aas_editor.widgets.dropfilebox import DropFileQWebEngineView
from widgets.jsonEditor import JSONEditor


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

            pages_front = int(self.pages_front) if self.pages_front.isdigit() else 3
            pages_end = int(self.pages_end) if self.pages_end.isdigit() else 3

            if pages_front == -1 or pages_end == -1 or (pages_front + pages_end) >= len(docs):
                pass  # Use all pages
            else:
                docs = docs[:pages_front] + docs[-pages_end:]

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
        self.setWindowTitle("Edit LLM Extracted Answer")
        self.setMinimumSize(600, 400)
        layout = QVBoxLayout(self)
        self.text = JSONEditor(self)
        self.text.setText(answer)
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
        self.documentListLabel.setVisible(False)
        self.documentList = QListWidget(self)
        self.documentList.setMaximumHeight(150)
        self.documentList.setMinimumHeight(50)
        self.documentList.setToolTip("List of processed documents")
        self.documentList.setVisible(False)


        self.html_renderer = DropFileQWebEngineView(self, emptyViewMsg="Drop PDF file here",
                             description="Drop a PDF file to extract Handover Documentation (VDI 2770).")
        self.html_renderer.fileDropped.connect(self.processPdf)
        self.html_renderer.setMinimumHeight(200)

        self.apiKeyLineEdit = QLineEdit(self, toolTip="API Key for LLM service",
                                        placeholderText="Enter API Key here",
                                        echoMode=QLineEdit.EchoMode.Password)
        self.modelLineEdit = QLineEdit(self, toolTip="Choose model to use")
        self.providerLineEdit = QComboBox(self, toolTip="LLM Provider",
                                          currentIndexChanged=self.provider_changed)
        self.providerLineEdit.addItems([k for k in LLM_PROVIDERS.keys()])

        self.model_info_label = QLabel(self)
        self.model_info_label.setPixmap(INFO_ICON.pixmap(24, 24))
        self.model_info_label.setFixedSize(24, 24)
        self.model_info_label.setToolTip(
            "A custom model can be used, else the default model is being used.\nFor more information about models see \"https://js.langchain.com/docs/integrations/chat/\"")

        self.idLineEdit = QLineEdit(self, toolTip="ID of the generated Handover Documentation Submodel",
                                    placeholderText="Enter Submodel ID")

        self.chooseButton = QPushButton("Choose && Process PDF", self,
                                        toolTip="The selected PDF file will be processed and the extracted Handover Documentation will be shown.",
                                        clicked=self.chooseAndProcessPdf)

        self.pagesFrontLineEdit = QLineEdit(self,
                                            toolTip="Number of pages to use from the front of the document",
                                            placeholderText="Front X pages to analyze (default: all)")
        self.pagesFrontLineEdit.setValidator(QIntValidator())
        self.pagesEndLineEdit = QLineEdit(self, toolTip="Number of pages to use from the end of the document",
                                          placeholderText="End X pages to analyze (default: all)")
        self.pagesEndLineEdit.setValidator(QIntValidator())
        self.processingThread = None

        self.finishButton = QPushButton("Finish handover documentation", self)
        self.finishButton.setToolTip("Generate the handover documentation from the extracted documents.")
        self.finishButton.setEnabled(False)
        self.finishButton.clicked.connect(self.finish_handover_documentation)

        self._initLayout()

        self.documents = []

    def _initLayout(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(TOOL_DESCRIPTION, self))

        layout.addWidget(self.idLineEdit)

        # Layout for LLM provider and model
        layout_model = QHBoxLayout()
        layout_model.addWidget(self.providerLineEdit)
        layout_model.addWidget(self.modelLineEdit)
        layout_model.addWidget(self.model_info_label)
        layout.addLayout(layout_model)
        layout.addWidget(self.apiKeyLineEdit)

        # Layout for pages selection
        layout_pages = QHBoxLayout()
        layout_pages.addWidget(self.pagesFrontLineEdit)
        layout_pages.addWidget(self.pagesEndLineEdit)
        layout.addLayout(layout_pages)

        layout.addWidget(self.documentListLabel)
        layout.addWidget(self.documentList)

        layout.addWidget(self.html_renderer)

        layout.addWidget(self.chooseButton)
        layout.addWidget(self.finishButton)
        self.setLayout(layout)

    def chooseAndProcessPdf(self):
        file, _ = QFileDialog.getOpenFileName(self, "Open PDF file", filter="PDF Files (*.pdf)")
        if file:
            self.processPdf(file)

    def processPdf(self, file: str):
        self.current_file = file
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

        self.processingThread.start()

    def cleanup_thread(self):
        if self.processingThread:
            self.processingThread.quit()
            self.processingThread.wait()
            self.processingThread.deleteLater()
            self.processingThread = None

    def on_processing_error(self, error_message):
        self.html_renderer.setHtml(f"<div style='color:red;'>{error_message}</div>")
        self.cleanup_thread()

    def provider_changed(self):
        self.modelLineEdit.setPlaceholderText(LLM_PROVIDERS[self.providerLineEdit.currentText()]["default_model"])

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
        self.cleanup_thread()
        dialog = AnswerDialog(answer, self)

        while dialog.exec():
            try:
                # 2. Open the file with the default OS handler
                file_url = QUrl.fromLocalFile(os.path.abspath(self.current_file))
                if not QDesktopServices.openUrl(file_url):
                    logging.warning(f"Could not open file: {self.current_file}")
                json_str = dialog.text.text()
                document = json2document(json_str)
                self.documents.append(document)

                item = QListWidgetItem(os.path.basename(self.current_file))
                item.setToolTip(self.current_file)
                self.documentList.addItem(item)
                self.documentList.setVisible(True)
                self.documentListLabel.setVisible(True)
                self._update_document_list_height()

                self.finishButton.setEnabled(True)

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
        if not self.documents:
            messsageBoxes.ErrorMessageBox(self, "No documents extracted!").exec()
            return
        id_ = self.idLineEdit.text() if self.idLineEdit.text() else "None"
        handover_sm = documents2handover_documentation(self.documents, id_=id_)
        normalized_json = json.dumps(handover_sm, cls=AASToJsonEncoder)
        normalized_json = normalized_json.replace('\\', '\\\\')
        normalized_handover_sm = json.loads(normalized_json, cls=AASFromJsonDecoder)

        self.handoverExtracted.emit(normalized_handover_sm)
        self.accept()
