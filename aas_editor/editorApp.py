from . import design

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMenu, QMessageBox
from PyQt5.QtCore import QFile, QTextStream
from PyQt5.QtGui import QKeySequence

from .qcomboboxenumdelegate import QComboBoxEnumDelegate

from .qt_models import *
from.settings import *



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
        self.pushButton_2.setDisabled(True)

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
        # todo delete
        self.comboBox.currentTextChanged.connect(self.toggleTheme)
        self.actionLight.triggered.connect(self.setLightTheme)
        self.actionDark.triggered.connect(self.setDarkTheme)
        self.detailInfoTreeView.expanded.connect(self.hideDetailInfoParentRow)
        self.detailInfoTreeView.collapsed.connect(self.showDetailInfoRowVal)

        self.packageItemsTreeView.customContextMenuRequested.connect(self.openPackageItemMenu)

    def openPackageItemMenu(self, position):
        print(self.packageItemsTreeView.selectedIndexes())
        indexes = self.packageItemsTreeView.selectedIndexes()
        index = QModelIndex() if not indexes else indexes[0]

        menu = QMenu()
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
            print(action.text())
            if action.text() == "Add package":
                self.addPackageWithDialog()
            elif action.text() == "Add shell":
                self.addShell()
            elif action.text() == "Add asset":
                self.addAssetWithDialog(index.data(PACKAGE_ROLE))
            elif action.text() == "Add submodel":
                self.addSubmodel()
            elif action.text() == "Add concept description":
                self.addConceptDescr()

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
        # self.detailInfoTreeView.expandAll()
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

    def addPackageWithDialog(self):
        dialog = AddPackageDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.addPackage(name=dialog.nameLineEdit.text())
        else:
            print("package adding cancelled")
        dialog.deleteLater()

    def addPackage(self, name="", objStore=None):
        package = Package(objStore)
        self.packageTreeViewModel.addItem(PackageTreeViewItem(obj=package, package=package, objName=name), QModelIndex())
        print("package added")

    def addShell(self):
        pass

    def addAssetWithDialog(self, package):
        dialog = AddAssetDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            kind = eval(dialog.kindComboBox.currentText())
            identification = Identifier(dialog.idLineEdit.text(), eval(dialog.idTypeComboBox.currentText()))
            self.addAsset(package, kind, identification)
        else:
            print("asset adding cancelled")
        dialog.deleteLater()

    def addAsset(self, package, kind, identification):
        asset = Asset(kind, identification)
        package.addAsset(asset)
        self.packageTreeViewModel.addItem(PackageTreeViewItem(obj=asset, package=package), QModelIndex())
        print("asset added")

    def addSubmodel(self):
        pass

    def addConceptDescr(self):
        pass


class Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.buttonOk = QtWidgets.QPushButton('Ok', self)
        self.buttonOk.clicked.connect(self.accept)
        self.buttonOk.setDisabled(True)
        self.buttonCancel = QtWidgets.QPushButton('Cancel', self)
        self.buttonCancel.clicked.connect(self.reject)
        self.layout = QtWidgets.QGridLayout(self)
        self.layout.addWidget(self.buttonOk, 10, 0)
        self.layout.addWidget(self.buttonCancel, 10, 1)


class AddPackageDialog(Dialog):
    def __init__(self, parent=None):
        Dialog.__init__(self, parent)
        self.setWindowTitle("Add Package")
        self.nameLabel = QtWidgets.QLabel(self)
        self.nameLabel.setText("Package name:")
        self.nameLineEdit = QtWidgets.QLineEdit(self)
        self.nameLineEdit.textChanged.connect(self.validate)
        self.layout.addWidget(self.nameLabel, 0, 0)
        self.layout.addWidget(self.nameLineEdit, 0, 1)

    def validate(self, nameText):
        if nameText:
            self.buttonOk.setDisabled(False)
        else:
            self.buttonOk.setDisabled(True)

class AddAssetDialog(Dialog):
    def __init__(self, parent=None):
        Dialog.__init__(self, parent)
        self.setWindowTitle("Add asset")

        self.kindLabel = QtWidgets.QLabel(self)
        self.kindLabel.setText("Kind:")
        self.kindComboBox = QtWidgets.QComboBox(self)
        currItem = base.AssetKind.INSTANCE
        items = [str(member) for member in type(currItem)]
        self.kindComboBox.addItems(items)
        self.kindComboBox.setCurrentText(str(currItem))

        self.idTypeLabel = QtWidgets.QLabel(self)
        self.idTypeLabel.setText("id_type:")
        self.idTypeComboBox = QtWidgets.QComboBox(self)
        currItem = base.IdentifierType.IRI
        items = [str(member) for member in type(currItem)]
        self.idTypeComboBox.addItems(items)
        self.idTypeComboBox.setCurrentText(str(currItem))

        self.idLabel = QtWidgets.QLabel(self)
        self.idLabel.setText("id:")
        self.idLineEdit = QtWidgets.QLineEdit(self)
        self.idLineEdit.textChanged.connect(self.validate)

        self.layout.addWidget(self.kindLabel, 0, 0)
        self.layout.addWidget(self.kindComboBox, 0, 1)
        self.layout.addWidget(self.idTypeLabel, 1, 0)
        self.layout.addWidget(self.idTypeComboBox, 1, 1)
        self.layout.addWidget(self.idLabel, 2, 0)
        self.layout.addWidget(self.idLineEdit, 2, 1)

    def validate(self, nameText):
        if nameText:
            self.buttonOk.setDisabled(False)
        else:
            self.buttonOk.setDisabled(True)


# ToDo logs insteads of prints
