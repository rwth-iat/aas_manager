from . import design

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .dialogs import AddPackDialog, AddAssetDialog

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

        self.packTreeViewModel = StandardTable()
        self.packItemsTreeView.setHeaderHidden(True)
        self.packItemsTreeView.setModel(self.packTreeViewModel)

        self.tabWidget.addTab(Tab(parent=self.tabWidget), "Welcome")

        self.packMenu = QMenu(self.packItemsTreeView)
        self.detailInfoMenu = QMenu()
        self.buildHandlers()

    def initToolbar(self):
        self.backAct = QAction(QIcon.fromTheme("go-previous"), "Back", self)
        self.backAct.setDisabled(True)
        self.backAct.setShortcut(QKeySequence.Back)
        self.backAct.triggered.connect(self.tabWidget.openPrevItem)

        self.forwardAct = QAction(QIcon.fromTheme("go-next"), "Forward", self)
        self.forwardAct.setDisabled(True)
        self.forwardAct.setShortcut(QKeySequence.Forward)
        self.forwardAct.triggered.connect(self.tabWidget.openNextItem)

        self.toolBar.addAction(self.backAct)
        self.toolBar.addAction(self.forwardAct)


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
        self.packItemsTreeView.selectionModel().currentChanged.connect(lambda packItem: self.tabWidget.openPackItemTab(packItem, newTab=False))
        self.packItemsTreeView.wheelClicked.connect(lambda packItem: self.tabWidget.openPackItemTab(packItem, setCurrent=False))
        self.packItemsTreeView.selectionModel().currentChanged.connect(self.updatePackItemContextMenu)
        self.packItemsTreeView.customContextMenuRequested.connect(self.openPackItemMenu)

        self.actionLight.triggered.connect(lambda: toggleTheme("light"))
        self.actionDark.triggered.connect(lambda: toggleTheme("dark"))

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
            self.packMenu.addAction(self.tr("Add submodel"))  # todo implement add submodel

        elif isinstance(index.data(OBJECT_ROLE), Submodel) or index.data(
                Qt.DisplayRole) == "concept_descriptions":
            self.packMenu.addAction(
                self.tr("Add concept description"))  # todo implement add concept descr

    def openPackItemMenu(self, point):  # todo resolve issue with action overload of ctrl+N
        self.packMenu.exec_(self.packItemsTreeView.viewport().mapToGlobal(point))

    def addPackWithDialog(self):
        dialog = AddPackDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.addPack(name=dialog.nameLineEdit.text())
        else:
            print("Package adding cancelled")
        dialog.deleteLater()

    def addPack(self, name="", objStore=None):
        pack = Package(objStore)
        self.packTreeViewModel.addItem(PackTreeViewItem(obj=pack, objName=name), QModelIndex())

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
            kind = eval(dialog.kindComboBox.currentText())
            identification = Identifier(dialog.idLineEdit.text(),
                                        eval(dialog.idTypeComboBox.currentText()))
            asset = Asset(kind, identification)
            self.addAsset(index, asset)
        else:
            print("asset adding cancelled")
        dialog.deleteLater()

    def addAsset(self, index, asset):
        index.data(PACKAGE_ROLE).add(asset)
        if index.data(Qt.DisplayRole) == "assets":
            assets = index
        elif index.parent().data(Qt.DisplayRole) == "assets":
            assets = index.parent()
        item = self.packTreeViewModel.addItem(PackTreeViewItem(obj=asset), assets)
        self.packItemsTreeView.setFocus()
        self.packItemsTreeView.setCurrentIndex(item)
        print("asset added")

    def addSubmodel(self):
        pass

    def addConceptDescr(self):
        pass

# ToDo logs insteads of prints
