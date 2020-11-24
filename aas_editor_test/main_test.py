import sys
from enum import Enum
from time import sleep
from unittest import TestCase

from PyQt5.QtCore import QModelIndex, QThread, QEventLoop, QTimer
from PyQt5.QtWidgets import QApplication
from aas.examples.data.example_aas import create_full_example
from aas.model import AASReference, Reference, Submodel, IdentifierType, Referable

from aas_editor.editorApp import EditorApp
from aas_editor.settings import DEFAULT_THEME, NAME_ROLE, VALUE_COLUMN
from aas_editor.widgets.tab import Tab
from aas_editor.widgets.treeview_pack import PackTreeView


class TestUi(TestCase):
    def setUp(self) -> None:
        self.app = QApplication(sys.argv)

        obj_store = create_full_example()

        self.window = EditorApp()
        from aas_editor.models import Package
        self.window.packTreeModel.addItem(Package("aas_files/TestPackage.aasx"))
        self.window.show()

        self.packTreeView: PackTreeView = self.window.packTreeView
        self.packTreeView.expandAll()
        self.tab1: Tab = self.window.mainTabWidget.widget(0)
        self.attrsTreeView = self.tab1.attrsTreeView

        self.itemsGenerator = self.packTreeView.model().iterItems()
        self.attrsGenerator = None

        # QTimer.singleShot(1000, test1)
        self.timer = QTimer()
        self.timer.setInterval(0)

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
            sleep(1)
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
            sleep(1)
            print("Test is completed")

    # def testEditCreate(self):
    #     self._startTest(self._testEditCreate)

    def _testEditCreate(self):
        currIndex = self.attrsTreeView.currentIndex()
        print(currIndex.data(NAME_ROLE))
        try:
            try:
                if self.attrsTreeView.editCreateAct.isEnabled():
                    # Edit current item if possible
                    self.attrsTreeView.editCreateAct.trigger()
                    if self.app.activeWindow():
                        self.app.activeWindow().close()
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
            sleep(1)
            print("Test is completed")

    def _startTest(self, testFunc):
        self.timer.timeout.connect(testFunc)
        self.timer.start()
        self.assertEqual(self.app.exec(), 0)

    def _nextItemInLeftTree(self):
        pack_index = next(self.itemsGenerator)
        self.packTreeView.setCurrentIndex(pack_index)
        self.attrsGenerator = self.attrsTreeView.model().iterItems()

    def _nextItemInRightTree(self):
        if not self.attrsGenerator:
            raise StopIteration("Generator is empty")
        attrIndex = next(self.attrsGenerator)
        self.attrsTreeView.setCurrentIndex(attrIndex)
