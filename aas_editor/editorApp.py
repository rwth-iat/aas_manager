from . import design

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMenu, QMessageBox
from PyQt5.QtCore import QFile, QTextStream

from .dialogs import AddPackageDialog, AddAssetDialog, AddDescriptionDialog
from .qcomboboxenumdelegate import QComboBoxEnumDelegate

from .qt_models import *
from.settings import *
from .util import getAttrDescription


class EditorApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.toggleTheme(PREFERED_THEME)

        self.packageTreeViewModel = StandardTable()
        self.packageItemsTreeView.setHeaderHidden(True)
        self.packageItemsTreeView.setModel(self.packageTreeViewModel)

        self.detailedInfoModel = DetailedInfoTable()
        self.detailInfoTreeView.setModel(self.detailedInfoModel)
        self.detailInfoTreeView.setColumnWidth(ATTRIBUTE_COLUMN, ATTR_COLUMN_WIDTH)

        self.buildHandlers()

    def importTestPackage(self, objStore):
        self.addPackage("TestPackage", objStore)

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
        self.packageItemsTreeView.selectionModel().currentChanged.connect(self.showPackageItemDetailedInfo)
        self.detailedInfoModel.valueChangeFailed.connect(self.itemDataChangeFailed)

        self.actionLight.triggered.connect(self.setLightTheme)
        self.actionDark.triggered.connect(self.setDarkTheme)

        self.detailInfoTreeView.expanded.connect(self.hideDetailInfoParentRow)
        self.detailInfoTreeView.collapsed.connect(self.showDetailInfoRowVal)

        self.packageItemsTreeView.customContextMenuRequested.connect(self.openPackageItemMenu)
        self.detailInfoTreeView.customContextMenuRequested.connect(self.openDetailInfoItemMenu)

    def showDetailInfoItemDescr(self, detailInfoItem):
        attr = detailInfoItem.data(NAME_ROLE)
        parent_obj = detailInfoItem.parent().data(OBJECT_ROLE)
        descr = getAttrDescription(attr, parent_obj.__init__.__doc__)
        self.descrLabel.setText(descr)

    def openPackageItemMenu(self, position):
        indexes = self.packageItemsTreeView.selectedIndexes()
        index = QModelIndex() if not indexes else indexes[0]

        menu = QMenu()
        addPackageAction, addShellAction, addAssetAction, addSubmodelAction, addConceptDescrAction = (None,)*5
        if isinstance(index.data(Qt.UserRole), Package) or not index.isValid():
            addPackageAction = menu.addAction(self.tr("Add package"))
        elif isinstance(index.data(Qt.UserRole), AssetAdministrationShell) or index.data(Qt.DisplayRole) == "shells":
            addShellAction = menu.addAction(self.tr("Add shell"))
        elif isinstance(index.data(Qt.UserRole), Asset) or index.data(Qt.DisplayRole) == "assets":
            addAssetAction = menu.addAction(self.tr("Add asset"))
        elif isinstance(index.data(Qt.UserRole), Submodel) or index.data(Qt.DisplayRole) == "submodels":
            addSubmodelAction = menu.addAction(self.tr("Add submodel"))
        elif isinstance(index.data(Qt.UserRole), Submodel) or index.data(Qt.DisplayRole) == "concept_descriptions":
            addConceptDescrAction = menu.addAction(self.tr("Add concept description"))
        action = menu.exec_(self.packageItemsTreeView.viewport().mapToGlobal(position))

        if action:
            if action == addPackageAction:
                self.addPackageWithDialog()
            elif action == addShellAction:
                self.addShell()
            elif action == addAssetAction:
                self.addAssetWithDialog(index)
            elif action == addSubmodelAction:
                self.addSubmodel()
            elif action == addConceptDescrAction:
                self.addConceptDescr()

    def openDetailInfoItemMenu(self, position):
        indexes = self.detailInfoTreeView.selectedIndexes()
        index = QModelIndex() if not indexes else indexes[0]

        menu = QMenu()
        if index.data(NAME_ROLE) == "description":
            addDescrAction = menu.addAction(self.tr("Add description"))
        action = menu.exec_(self.detailInfoTreeView.viewport().mapToGlobal(position))

        if action:
            if action == addDescrAction:
                self.addDescrWithDialog(index)

    def hideDetailInfoParentRow(self, index):
        if self.detailedInfoModel.objByIndex(index).children():
            self.detailedInfoModel.hideRowVal(index)

    def showDetailInfoRowVal(self, index):
        self.detailedInfoModel.showRowVal(index)

    def showPackageItemDetailedInfo(self, packageItem):
        self.detailedInfoModel = DetailedInfoTable(mainObj=packageItem.data(Qt.UserRole), package=packageItem.data(PACKAGE_ROLE))
        self.pathLabel.setText(self.getPackageItemPath(packageItem))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), packageItem.data(Qt.DisplayRole))
        self.detailInfoTreeView.setModel(self.detailedInfoModel)
        self.detailInfoTreeView.selectionModel().currentChanged.connect(self.showDetailInfoItemDescr)
        self.detailInfoTreeView.setItemDelegate(QComboBoxEnumDelegate())
        self.detailedInfoModel.valueChangeFailed.connect(self.itemDataChangeFailed)

    def getPackageItemPath(self, treeItem):
        path = treeItem.data(Qt.DisplayRole)
        while treeItem.parent().isValid():
            treeItem = treeItem.parent()
            path = f"{treeItem.data(Qt.DisplayRole)}/{path}"
        return path

    def itemDataChangeFailed(self, msg):
        QMessageBox.critical(self, "Error",msg)

    def setLightTheme(self):
        self.toggleTheme("light")

    def setDarkTheme(self):
        self.toggleTheme("dark")

    def toggleTheme(self, theme):
        if theme in THEMES:
            self.toggleStylesheet(THEMES[theme])

    def toggleStylesheet(self, path):
        '''
        Toggle the stylesheet to use the desired path in the Qt resource
        system (prefixed by `:/`) or generically (a path to a file on
        system).

        :path:      A full path to a resource or file on system
        '''

        # get the QApplication instance,  or crash if not set
        app = QApplication.instance()
        if app is None:
            raise RuntimeError("No Qt Application found.")

        file = QFile(path)
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)
        app.setStyleSheet(stream.readAll())

    def addDescrWithDialog(self, index):
        dialog = AddDescriptionDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            lang = dialog.langLineEdit.text()
            descr = dialog.descrLineEdit.text()
            self.detailedInfoModel.addItem(DetailedInfoItem(obj=descr, name=lang), index)
        else:
            print("asset adding cancelled")
        dialog.deleteLater()

    def addPackageWithDialog(self):
        dialog = AddPackageDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.addPackage(name=dialog.nameLineEdit.text())
        else:
            print("package adding cancelled")
        dialog.deleteLater()

    def addPackage(self, name="", objStore=None):
        package = Package(objStore)
        self.packageTreeViewModel.addItem(PackageTreeViewItem(obj=package, objName=name), QModelIndex())

    def addShellWithDialog(self):
        dialog = AddShellDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            kind = eval(dialog.assetComboBox.currentText())
            identification = Identifier(dialog.idLineEdit.text(), eval(dialog.idTypeComboBox.currentText()))
            shell = AssetAdministrationShell(shell, identification)
            self.addShell(index, shell)
        else:
            print("asset adding cancelled")
        dialog.deleteLater()

    def addShell(self, index, shell):
        index.data(PACKAGE_ROLE).addShell(shell)
        if index.data(Qt.DisplayRole) == "shells":
            shells = index
        elif index.parent().data(Qt.DisplayRole) == "shells":
            shells = index.parent()
        self.packageTreeViewModel.addItem(PackageTreeViewItem(obj=shell), shells)
        print("shell added")

    def addAssetWithDialog(self, index):
        dialog = AddAssetDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
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
        self.packageTreeViewModel.addItem(PackageTreeViewItem(obj=asset), assets)
        print("asset added")

    def addSubmodel(self):
        pass

    def addConceptDescr(self):
        pass

# ToDo logs insteads of prints
