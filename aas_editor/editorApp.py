from . import design

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


from .dialogs import AddPackDialog, AddAssetDialog, AddDescriptionDialog
from .qcomboboxenumdelegate import QComboBoxEnumDelegate

from .qt_models import *
from.settings import *
from .util import getAttrDoc, getTreeItemPath, toggleStylesheet, toggleTheme


class EditorApp(QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        toggleTheme(PREFERED_THEME)

        self.packTreeViewModel = StandardTable()
        self.packItemsTreeView.setHeaderHidden(True)
        self.packItemsTreeView.setModel(self.packTreeViewModel)

        self.detailedInfoModel = DetailedInfoTable()
        self.detailInfoTreeView.setModel(self.detailedInfoModel)
        self.detailInfoTreeView.setColumnWidth(ATTRIBUTE_COLUMN, ATTR_COLUMN_WIDTH)

        self.packMenu = QMenu(self.packItemsTreeView)
        self.detailInfoMenu = QMenu(self.detailInfoTreeView)
        self.buildHandlers()

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
        self.packItemsTreeView.selectionModel().currentChanged.connect(self.showPackItemDetailInfo)
        self.packItemsTreeView.selectionModel().currentChanged.connect(self.updatePackItemContextMenu)
        self.packItemsTreeView.customContextMenuRequested.connect(self.openPackItemMenu)

        self.detailInfoTreeView.selectionModel().currentChanged.connect(self.updateDetailInfoItemMenu)
        self.detailInfoTreeView.customContextMenuRequested.connect(self.openDetailInfoItemMenu)
        self.detailInfoTreeView.selectionModel().currentChanged.connect(self.showDetailInfoItemDoc)
        self.detailInfoTreeView.setItemDelegate(QComboBoxEnumDelegate())
        self.detailedInfoModel.valueChangeFailed.connect(self.itemDataChangeFailed)

        self.actionLight.triggered.connect(lambda: toggleTheme("light"))
        self.actionDark.triggered.connect(lambda: toggleTheme("dark"))

        self.detailInfoTreeView.expanded.connect(self.detailedInfoModel.hideRowVal)
        self.detailInfoTreeView.collapsed.connect(self.detailedInfoModel.showRowVal)

    def showDetailInfoItemDoc(self, detailInfoItem):
        attr = detailInfoItem.data(NAME_ROLE)
        if detailInfoItem.parent().isValid():
            parent_obj = detailInfoItem.parent().data(OBJECT_ROLE)
        else:
            parent_obj = self.detailedInfoModel.objByIndex(detailInfoItem).masterObj
        doc = getAttrDoc(attr, parent_obj.__init__.__doc__)
        self.descrLabel.setText(doc)

    def updatePackItemContextMenu(self, index):
        self.packMenu.clear()
        for a in self.packItemsTreeView.actions():
            self.packItemsTreeView.removeAction(a)

        if isinstance(index.data(OBJECT_ROLE), Package) or not index.isValid():
            act = self.packMenu.addAction(self.tr("Add package"), self.addPackWithDialog, QKeySequence.New)
            self.packItemsTreeView.addAction(act)

        elif isinstance(index.data(OBJECT_ROLE), AssetAdministrationShell) or index.data(Qt.DisplayRole) == "shells":
            act = self.packMenu.addAction(self.tr("Add shell"), lambda i=index: self.addShellWithDialog(i), QKeySequence.New)
            self.packItemsTreeView.addAction(act)

        elif isinstance(index.data(OBJECT_ROLE), Asset) or index.data(Qt.DisplayRole) == "assets":
            act = self.packMenu.addAction(self.tr("Add asset"), lambda i=index: self.addAssetWithDialog(i), QKeySequence.New)
            self.packItemsTreeView.addAction(act)

        elif isinstance(index.data(OBJECT_ROLE), Submodel) or index.data(Qt.DisplayRole) == "submodels":
            self.packMenu.addAction(self.tr("Add submodel")) # todo implement add submodel

        elif isinstance(index.data(OBJECT_ROLE), Submodel) or index.data(Qt.DisplayRole) == "concept_descriptions":
            self.packMenu.addAction(self.tr("Add concept description"))  # todo implement add concept descr

    def openPackItemMenu(self, point):
        self.packMenu.exec_(self.packItemsTreeView.viewport().mapToGlobal(point))

    def updateDetailInfoItemMenu(self, index):
        self.detailInfoMenu.clear()
        print("p ",self.packItemsTreeView.actions())
        print("b ",self.detailInfoTreeView.actions())
        for a in self.detailInfoTreeView.actions():
            self.detailInfoTreeView.removeAction(a)
        print("p ",self.packItemsTreeView.actions())
        print(self.detailInfoTreeView.actions())

        if index.data(NAME_ROLE) == "description":
            act = self.detailInfoMenu.addAction(self.tr("Add description"), lambda i=index: self.addDescrWithDialog(i), QKeySequence.New)
            self.detailInfoTreeView.addAction(act)

    def openDetailInfoItemMenu(self, point):
        self.detailInfoMenu.exec_(self.detailInfoTreeView.viewport().mapToGlobal(point))

    def showPackItemDetailInfo(self, packItem):
        self.detailedInfoModel = DetailedInfoTable(mainObj=packItem.data(OBJECT_ROLE), package=packItem.data(PACKAGE_ROLE))
        self.pathLabel.setText(getTreeItemPath(packItem))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), packItem.data(Qt.DisplayRole))
        self.detailInfoTreeView.setModel(self.detailedInfoModel)
        self.detailInfoTreeView.setItemDelegate(QComboBoxEnumDelegate())
        self.buildHandlers()

    def itemDataChangeFailed(self, msg):
        QMessageBox.critical(self, "Error",msg)

    def addDescrWithDialog(self, index):
        dialog = AddDescriptionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            lang = dialog.langLineEdit.text()
            descr = dialog.descrLineEdit.text()
            self.detailedInfoModel.addItem(DetailedInfoItem(obj=descr, name=lang), index)
        else:
            print("asset adding cancelled")
        dialog.deleteLater()

    def addPackWithDialog(self):
        dialog = AddPackDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.addPack(name=dialog.nameLineEdit.text())
        else:
            print("package adding cancelled")
        dialog.deleteLater()

    def addPack(self, name="", objStore=None):
        pack = Package(objStore)
        self.packTreeViewModel.addItem(PackageTreeViewItem(obj=pack, objName=name), QModelIndex())

    def addShellWithDialog(self, index):
        dialog = None # todo impelement AddShellDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            kind = eval(dialog.assetComboBox.currentText())
            identification = Identifier(dialog.idLineEdit.text(), eval(dialog.idTypeComboBox.currentText()))
            #shell = AssetAdministrationShell(asset, identification)
            #self.addShell(index, shell)
        else:
            print("asset adding cancelled")
        dialog.deleteLater()

    def addShell(self, index, shell):
        index.data(PACKAGE_ROLE).addShell(shell)
        if index.data(Qt.DisplayRole) == "shells":
            shells = index
        elif index.parent().data(Qt.DisplayRole) == "shells":
            shells = index.parent()
        self.packTreeViewModel.addItem(PackageTreeViewItem(obj=shell), shells)
        print("shell added")

    def addAssetWithDialog(self, index):
        dialog = AddAssetDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            kind = eval(dialog.kindComboBox.currentText())
            identification = Identifier(dialog.idLineEdit.text(), eval(dialog.idTypeComboBox.currentText()))
            asset = Asset(kind, identification)
            self.addAsset(index, asset)
        else:
            print("asset adding cancelled")
        dialog.deleteLater()

    def addAsset(self, index, asset):
        index.data(PACKAGE_ROLE).addAsset(asset)
        if index.data(Qt.DisplayRole) == "assets":
            assets = index
        elif index.parent().data(Qt.DisplayRole) == "assets":
            assets = index.parent()
        item = self.packTreeViewModel.addItem(PackageTreeViewItem(obj=asset), assets)
        self.packItemsTreeView.setFocus()
        self.packItemsTreeView.setCurrentIndex(item)
        print("asset added")

    def addSubmodel(self):
        pass

    def addConceptDescr(self):
        pass

# ToDo logs insteads of prints
