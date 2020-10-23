import sys
from enum import Enum
from time import sleep
from unittest import TestCase

from PyQt5.QtCore import QModelIndex, QThread, QEventLoop, QTimer
from PyQt5.QtWidgets import QApplication
from aas.examples.data.example_aas import create_full_example
from aas.model import AASReference, Reference, Submodel, IdentifierType, Referable

from aas_editor.editorApp import EditorApp
from aas_editor.settings import PREFERED_THEME, NAME_ROLE
from aas_editor.util import toggleTheme
from aas_editor.views.tab import Tab
from aas_editor.views.treeview_pack import PackTreeView

app = QApplication(sys.argv)

class TestUtilFuncs(TestCase):
    def test_main(self):
        def test1():
            packTreeView.show()
            packTreeView.expandAll()
            window.show()

            tab1: Tab = window.tabWidget.widget(0)
            attrsTreeView = tab1.attrsTreeView

            for pack_index in packTreeView.model().iterItems():
                window.show()
                packTreeView.setCurrentIndex(pack_index)
                # for attr_index in tab1.attrsTreeView.model().iterItems():
                #     window.show()
                #     attrsTreeView.setCurrentIndex(attr_index)
                #     print("   ", attr_index.data(NAME_ROLE))
                #     sleep(0.5)
                # print(pack_index.data(NAME_ROLE))

        obj_store = create_full_example()

        window = EditorApp()
        toggleTheme(PREFERED_THEME)
        window.importTestPack(obj_store)
        window.show()

        packTreeView: PackTreeView = window.packItemsTreeView
        packTreeView.expandAll()

        # QTimer.singleShot(1000, test1)
        timer = QTimer()
        timer.setInterval(500)
        timer.timeout.connect(test1)
        timer.start()
        app.exec_()
