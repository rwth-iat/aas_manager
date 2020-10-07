from . import design

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .dialogs import AddPackDialog, AddAssetDialog, AddObjDialog

from .qt_models import *
from .qt_views import Tab
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

    def updatePackItemContextMenu(self, index):
        self.packMenu.clear()
        for a in self.packItemsTreeView.actions():
            self.packItemsTreeView.removeAction(a)

        if isinstance(index.data(OBJECT_ROLE), Package) or not index.isValid():
            act = self.packMenu.addAction(self.tr("Add package"), self.addPackWithDialog,
                                          QKeySequence.New)
            self.packItemsTreeView.addAction(act)

        elif isinstance(index.data(OBJECT_ROLE), AssetAdministrationShell) or index.data(
                Qt.DisplayRole) == "shells":
            act = self.packMenu.addAction(self.tr("Add shell"),
                                          lambda i=index: self.addShellWithDialog(i),
                                          QKeySequence.New)
            self.packItemsTreeView.addAction(act)

        elif isinstance(index.data(OBJECT_ROLE), Asset) or index.data(Qt.DisplayRole) == "assets":
            act = self.packMenu.addAction(self.tr("Add asset"),
                                          lambda i=index: self.addAssetWithDialog(i),
                                          QKeySequence.New)
            self.packItemsTreeView.addAction(act)

        elif isinstance(index.data(OBJECT_ROLE), Submodel) or index.data(
                Qt.DisplayRole) == "submodels":
            self.packMenu.addAction(self.tr("Add submodel"),
                                    lambda i=index: self.addItemWithDialog(i, Submodel, objName="Submodel"))  # todo implement add submodel

        elif isinstance(index.data(OBJECT_ROLE), Submodel) or index.data(
                Qt.DisplayRole) == "concept_descriptions":
            self.packMenu.addAction(
                self.tr("Add concept description"))  # todo implement add concept descr

    def addItemWithDialog(self, index, objType, objName=""):
        dialog = AddObjDialog(objType, self, objName=objName)
        if dialog.exec_() == QDialog.Accepted:
            obj = dialog.getObj2add()
            item = self.packTreeViewModel.addItem(PackTreeViewItem(obj=obj), index)
        else:
            print("Item adding cancelled")
        dialog.deleteLater()
        self.packItemsTreeView.setFocus()
        self.packItemsTreeView.setCurrentIndex(item)

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

    def addShellWithDialog(self, index):
        dialog = None  # todo impelement AddShellDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            kind = eval(dialog.assetComboBox.currentText())
            identification = Identifier(dialog.idLineEdit.text(), eval(
                dialog.idTypeComboBox.currentText()))  # shell = AssetAdministrationShell(asset, identification)  # self.addShell(index, shell)
        else:
            print("asset adding cancelled")
        dialog.deleteLater()

    def addShell(self, index, shell):
        index.data(PACKAGE_ROLE).add(shell)
        if index.data(Qt.DisplayRole) == "shells":
            shells = index
        elif index.parent().data(Qt.DisplayRole) == "shells":
            shells = index.parent()
        self.packTreeViewModel.addItem(PackTreeViewItem(obj=shell), shells)
        print("shell added")

    def addAssetWithDialog(self, index):
        dialog = AddAssetDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            asset = dialog.getObj2add()
            self.addAsset(index, asset)
        else:
            print("asset adding cancelled")
        dialog.deleteLater()

    def addAsset(self, index, asset):
        if index.data(Qt.DisplayRole) == "assets":
            parent = index
        elif index.parent().data(Qt.DisplayRole) == "assets":
            parent = index.parent()
        item = self.packTreeViewModel.addItem(PackTreeViewItem(obj=asset), parent)
        self.packItemsTreeView.setFocus()
        self.packItemsTreeView.setCurrentIndex(item)
        print("asset added")

    def addSubmodel(self):
        pass

    def addConceptDescr(self):
        pass

# ToDo logs insteads of prints
