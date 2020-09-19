from . import design

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


from .dialogs import AddPackDialog, AddAssetDialog, AddDescriptionDialog
from .qcomboboxenumdelegate import QComboBoxEnumDelegate

from .qt_models import *
from.settings import *
from .util import getTreeItemPath, toggleTheme


class EditorApp(QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        toggleTheme(PREFERED_THEME)

        self.packTreeViewModel = StandardTable()
        self.packItemsTreeView.setHeaderHidden(True)
        self.packItemsTreeView.setModel(self.packTreeViewModel)

        self.tabWidget.addTab(Tab(parent=self.tabWidget), "Welcome")

        self.packMenu = QMenu(self.packItemsTreeView)
        self.detailInfoMenu = QMenu()
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
        # self.packItemsTreeView.selectionModel().currentChanged.connect(self.openPackItem)
        self.packItemsTreeView.doubleClicked.connect(self.openPackItem)
        self.tabWidget.tabCloseRequested.connect(self.removeTab)
        self.packItemsTreeView.selectionModel().currentChanged.connect(self.updatePackItemContextMenu)
        self.packItemsTreeView.customContextMenuRequested.connect(self.openPackItemMenu)

        self.actionLight.triggered.connect(lambda: toggleTheme("light"))
        self.actionDark.triggered.connect(lambda: toggleTheme("dark"))

    def openPackItem(self, packItem):
        tab = Tab(packItem, parent=self.tabWidget)
        self.tabWidget.addTab(tab, packItem.data(Qt.DisplayRole))
        self.tabWidget.setCurrentWidget(tab)

    def removeTab(self, index):
        #remove tab from widget
        widget = self.tabWidget.widget(index)
        if widget is not None:
            widget.deleteLater()
        self.tabWidget.removeTab(index)

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

    def openPackItemMenu(self, point):# todo resolve issue with action overload of ctrl+N
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
            identification = Identifier(dialog.idLineEdit.text(), eval(dialog.idTypeComboBox.currentText()))
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


class Tab(QWidget):
    def __init__(self, packItem=QModelIndex(), parent=None):
        super(Tab, self).__init__(parent)
        # self.pathLabel = QLabel(getTreeItemPath(packItem), self)
        self.pathLabel = QLineEdit(getTreeItemPath(packItem), self)
        self.pathLabel.setReadOnly(True)
        self.descrLabel = QLabel(self)
        self.detailInfoMenu = QMenu(self)
        self._initTreeView(packItem)
        self._initLayout()
        self.buildHandlers()

    def _initTreeView(self, packItem):
        self.detailInfoTreeView = QTreeView(self)
        self.detailInfoTreeView.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.detailInfoTreeView.sizePolicy().hasHeightForWidth())
        self.detailInfoTreeView.setSizePolicy(sizePolicy)
        self.detailInfoTreeView.setMinimumSize(QtCore.QSize(429, 0))
        self.detailInfoTreeView.setBaseSize(QtCore.QSize(429, 555))
        self.detailInfoTreeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.detailInfoTreeView.setFrameShape(QFrame.StyledPanel)
        self.detailInfoTreeView.setFrameShadow(QFrame.Sunken)
        self.detailInfoTreeView.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.detailInfoTreeView.setObjectName("detailInfoTreeView")

        self.detailedInfoModel = DetailedInfoTable(mainObj=packItem.data(OBJECT_ROLE),
                                  package=packItem.data(PACKAGE_ROLE))
        self.detailInfoTreeView.setModel(self.detailedInfoModel)
        self.detailInfoTreeView.setColumnWidth(ATTRIBUTE_COLUMN, ATTR_COLUMN_WIDTH)
        self.detailInfoTreeView.setItemDelegate(QComboBoxEnumDelegate())

    def _initLayout(self):
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.addWidget(self.descrLabel, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.detailInfoTreeView, 0, 0, 1, 1)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.addWidget(self.pathLabel)
        self.verticalLayout.addLayout(self.gridLayout)

    def buildHandlers(self):
        self.detailedInfoModel.valueChangeFailed.connect(self.itemDataChangeFailed)
        self.detailInfoTreeView.expanded.connect(self.detailedInfoModel.hideRowVal)
        self.detailInfoTreeView.collapsed.connect(self.detailedInfoModel.showRowVal)
        self.detailInfoTreeView.selectionModel().currentChanged.connect(self.updateDetailInfoItemMenu)
        self.detailInfoTreeView.customContextMenuRequested.connect(self.openDetailInfoItemMenu)
        self.detailInfoTreeView.selectionModel().currentChanged.connect(self.showDetailInfoItemDoc)
        self.detailInfoTreeView.setItemDelegate(QComboBoxEnumDelegate())

    def showDetailInfoItemDoc(self, detailInfoItem: QModelIndex):
        self.descrLabel.setText(detailInfoItem.data(Qt.ToolTipRole))

    def itemDataChangeFailed(self, msg):
        QMessageBox.critical(self, "Error", msg) # todo find out how to pass app, not Tab

    def updateDetailInfoItemMenu(self, index):
        self.detailInfoMenu.clear()
        # print("b ", self.actions())
        # for a in self.actions():
        #     self.removeAction(a)
        # print(self.actions())

        if index.data(NAME_ROLE) == "description":
            act = self.detailInfoMenu.addAction(self.tr("Add description"), lambda i=index: self.addDescrWithDialog(i), QKeySequence.New)
            self.addAction(act)

    def openDetailInfoItemMenu(self, point):
        self.detailInfoMenu.exec_(self.detailInfoTreeView.viewport().mapToGlobal(point))

    def addDescrWithDialog(self, index):
        dialog = AddDescriptionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            lang = dialog.langLineEdit.text()
            descr = dialog.descrLineEdit.text()
            self.detailedInfoModel.addItem(DetailedInfoItem(obj=descr, name=lang), index)
        else:
            print("Asset adding cancelled")
        dialog.deleteLater()