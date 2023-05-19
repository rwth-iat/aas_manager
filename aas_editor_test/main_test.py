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
from time import sleep
from unittest import TestCase

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from aas_editor.editorApp import EditorApp
from aas_editor.settings.app_settings import NAME_ROLE
from aas_editor.widgets import Tab, PackTreeView


class TestUi(TestCase):
    def setUp(self) -> None:
        self.app = QApplication(sys.argv)

        self.window = EditorApp()
        self.window.mainTreeView.createAndOpenPackFromFile("aas_files/TestPackage.aasx")
        self.window.show()

        self.packTreeView: PackTreeView = self.window.mainTreeView
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
        print(pack_index.data(NAME_ROLE))
        self.packTreeView.setCurrentIndex(pack_index)
        self.attrsGenerator = self.attrsTreeView.model().iterItems()

    def _nextItemInRightTree(self):
        if not self.attrsGenerator:
            raise StopIteration("Generator is empty")
        attrIndex = next(self.attrsGenerator)
        self.attrsTreeView.setCurrentIndex(attrIndex)
