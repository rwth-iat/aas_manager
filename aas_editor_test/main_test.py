#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/

import sys
import time
from pathlib import Path
from unittest import TestCase

import pytest
pytest.importorskip('PyQt6.QtWebEngineCore', reason='PyQt6.QtWebEngineCore not available')

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox

from aas_editor.editorApp import EditorApp
from aas_editor.settings.app_settings import NAME_ROLE
from aas_editor.treeviews.treeview_pack import PackTreeView
from aas_editor.widgets import TabWithTreeView

AASX_FILE = Path(__file__).parent / "aas_files" / "TestPackage.aasx"


class TestUi(TestCase):
    def setUp(self) -> None:
        # Class attribute: if the app were freed after a test, PyQt would delete
        # all Qt objects, including class-level ones like AddressLine.signal
        TestUi.app = QApplication.instance() or QApplication(sys.argv)
        self.window = EditorApp(fileToOpen=str(AASX_FILE))
        self.window.show()
        # The file is read in the background: wait until its pack is in the tree
        deadline = time.monotonic() + 30
        while self.window.mainTreeView.loadingFiles() and time.monotonic() < deadline:
            self.app.processEvents()
            time.sleep(0.005)
        self.assertIn(AASX_FILE.absolute(), self.window.packTreeModel.openedFiles())

        self.packTreeView: PackTreeView = self.window.mainTreeView
        self.packTreeView.expandAll()
        self.tab1: TabWithTreeView = self.window.mainTabWidget.widget(0)
        self.attrsTreeView = self.tab1.attrsTreeView

        self.itemsGenerator = self.packTreeView.model().iterItems()
        self.attrsGenerator = None

        self.timer = QTimer()
        self.timer.setInterval(0)
        # Dialogs block in exec(); close any that opens (also error boxes)
        self.modalCloser = QTimer(interval=50, timeout=self._closeModal)
        self.errors = []

    def tearDown(self) -> None:
        self.window.close()

    def testViews(self):
        self._startTest(self._testViews)

    def _testViews(self):
        try:
            try:
                self._nextItemInRightTree()
            except (StopIteration, TypeError):
                self._nextItemInLeftTree()
        except StopIteration:
            self.app.exit(0)
            print("Test is completed")

    def testLinks(self):
        self._startTest(self._testLinks)

    def _testLinks(self):
        currIndex = self.attrsTreeView.currentIndex()
        print(currIndex.data(NAME_ROLE))
        self.assertTrue(self.window.mainTabWidget.count() <= 2)
        try:
            try:
                if self.window.mainTabWidget.currentIndex() == 1:
                    # Tab of link item is opened
                    self.assertTrue(self.packTreeView.currentIndex().isValid())
                    self.assertNotEqual(self.currIterPackIndex.data(NAME_ROLE),
                                        self.packTreeView.currentIndex().data(NAME_ROLE))
                    self.window.mainTabWidget.removeTab(1)
                    return
                elif self.attrsTreeView.openInNewTabAct.isEnabled():
                    self.currIterPackIndex = self.packTreeView.currentIndex()
                    # Open link item in new tab
                    self.attrsTreeView.openInNewTabAct.trigger()
                    self._nextItemInRightTree()
                    return
                else:
                    self._nextItemInRightTree()
                    return
            except StopIteration as e:
                print(e)
                self._nextItemInLeftTree()
        except StopIteration:
            self.app.exit(0)
            print("Test is completed")

    def testEditCreate(self):
        self._startTest(self._testEditCreate)

    def _testEditCreate(self):
        currIndex = self.attrsTreeView.currentIndex()
        print(currIndex.data(NAME_ROLE))
        try:
            try:
                if self.attrsTreeView.editCreateInDialogAct.isEnabled():
                    # Edit current item if possible; the dialog is closed by
                    # modalCloser. Pause the test step meanwhile: the timer would
                    # fire inside the dialog's event loop and open more dialogs.
                    self.timer.stop()
                    self.attrsTreeView.editCreateInDialogAct.trigger()
                    self.timer.start()
                    self._nextItemInRightTree()
                    return
                else:
                    self._nextItemInRightTree()
                    return
            except StopIteration as e:
                print(e)
                self._nextItemInLeftTree()
        except StopIteration:
            self.app.exit(0)
            print("Test is completed")

    def _startTest(self, testFunc):
        self.timer.timeout.connect(testFunc)
        self.timer.start()
        self.modalCloser.start()
        self.assertEqual(self.app.exec(), 0)
        self.modalCloser.stop()
        self.assertEqual(self.errors, [], "Error boxes were shown")

    def _closeModal(self):
        dialog = QApplication.activeModalWidget()
        if isinstance(dialog, QMessageBox):
            self.errors.append(dialog.text())
        if isinstance(dialog, QDialog):
            # done(), not close(): a QMessageBox without Escape button ignores close
            dialog.done(QDialog.DialogCode.Rejected)

    def _nextItemInLeftTree(self):
        pack_index = next(self.itemsGenerator)
        print(pack_index.data(NAME_ROLE))
        self.packTreeView.setCurrentIndex(pack_index)
        self.attrsGenerator = self.attrsTreeView.model().iterItems()

    def _nextItemInRightTree(self):
        if not self.attrsGenerator:
            raise StopIteration("Generator is empty")
        attrIndex = next(self.attrsGenerator)
        self.attrsTreeView.setCurrentIndex(attrIndex)
