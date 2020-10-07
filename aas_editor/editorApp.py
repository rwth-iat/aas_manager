from PyQt5.QtCore import QModelIndex
from aas.model import AssetAdministrationShell, Asset, Submodel

from . import design

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .dialogs import AddObjDialog
from .models import PackTreeViewItem, Package, StandardTable, OBJECT_ROLE, PACKAGE_ROLE

from .views.tab import Tab
from .settings import *
from .util import toggleTheme


class EditorApp(QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        toggleTheme(PREFERED_THEME)
        self.initToolbar()
        self.switch2rightTreeSC = QShortcut(QKeySequence("Ctrl+Right"), self)
        self.switch2leftTreeSC = QShortcut(QKeySequence("Ctrl+Left"), self)

        self.packTreeViewModel = StandardTable()
        self.packItemsTreeView.setHeaderHidden(True)
        self.packItemsTreeView.setModel(self.packTreeViewModel)

        self.tabWidget.addTab(Tab(parent=self.tabWidget), "Welcome")

        self.buildHandlers()

        # todo: save, open , collapse all, expand all actions

    def initToolbar(self):
        self.toolBar.addAction(self.tabWidget.backAct)
        self.toolBar.addAction(self.tabWidget.forwardAct)

    def importTestPack(self, objStore):
        self.addPack("TestPackage", objStore)

    def iterItems(self, root):
        def recurse(parent):
            for row in range(parent.rowCount()):
                for column in range(parent.columnCount()):
                    child = parent.child(row, column)
                    yield child
                    if child.hasChildren():
                        yield from recurse(child)

        if root is not None:
            yield from recurse(root)

    def buildHandlers(self):
        self.tabWidget.currItemChanged.connect(self.packItemsTreeView.setCurrentIndex)

        self.packItemsTreeView.wheelClicked.connect(self.tabWidget.openItemInBackgroundTab)
        self.packItemsTreeView.openInBackgroundTabClicked.connect(self.tabWidget.openItemInBackgroundTab)
        self.packItemsTreeView.openInNewTabClicked.connect(self.tabWidget.openItemInNewTab)
        self.packItemsTreeView.openInCurrTabClicked.connect(self.tabWidget.openItem)
        self.packItemsTreeView.selectionModel().currentChanged.connect(self.tabWidget.openItem)

        self.actionLight.triggered.connect(lambda: toggleTheme("light"))
        self.actionDark.triggered.connect(lambda: toggleTheme("dark"))

        self.switch2rightTreeSC.activated.connect(self.setFocus2rightTree)
        self.switch2leftTreeSC.activated.connect(self.packItemsTreeView.setFocus)

    def setFocus2rightTree(self):
        tab: 'Tab' = self.tabWidget.currentWidget()
        if not tab.attrsTreeView.currentIndex().isValid():
            firstItem = tab.attrsTreeView.model().index(0, 0, QModelIndex())
            tab.attrsTreeView.setCurrentIndex(firstItem)
        self.tabWidget.currentWidget().attrsTreeView.setFocus()


    def addPackWithDialog(self):
        dialog = AddPackDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            pack = dialog.getObj2add()
            self.packTreeViewModel.addItem(PackTreeViewItem(obj=pack, objName=pack.name))
        else:
            print("Package adding cancelled")
        dialog.deleteLater()

    def addPack(self, name="", objStore=None):
        pack = Package(name=name, objStore=objStore)
        self.packTreeViewModel.addItem(PackTreeViewItem(obj=pack, objName=name))



# ToDo logs insteads of prints
