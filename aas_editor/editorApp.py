from . import design

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QFile, QTextStream
from .qcomboboxenumdelegate import QComboBoxEnumDelegate

from .qt_models import *

ATTR_COLUMN_WIDTH = 200

DARK_THEME_PATH = "themes/dark.qss"
LIGHT_THEME_PATH = "themes/light.qss"
#LIGHT_THEME_PATH = ":/aas_editor/light.qss"


class EditorApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setLightTheme()

        self.treeViewModel = StandardTable()
        self.aasItemsTreeView.setHeaderHidden(True)
        self.aasItemsTreeView.setModel(self.treeViewModel)

        self.detailedInfoModel = DetailedInfoTable()
        self.detailInfoTreeView.setModel(self.detailedInfoModel)
        self.detailInfoTreeView.setColumnWidth(ATTRIBUTE_COLUMN, ATTR_COLUMN_WIDTH)
        self.pushButton_2.setDisabled(True)

        self.objStore = None
        self.buildHandlers()

    def importPackage(self, objStore):
        self.objStore = objStore
        package = Package(objStore)
        self.treeViewModel.addItem(AasTreeViewItem(obj=package, objStore=objStore), QModelIndex())
        self.aasItemsTreeView.setModel(self.treeViewModel)

    def importShell(self, shell, objStore):
        self.objStore = objStore
        shellItem = AasTreeViewItem(obj=shell, objStore=objStore)
        self.treeViewModel.addItem(shellItem, QModelIndex())
        self.aasItemsTreeView.setModel(self.treeViewModel)

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
        self.aasItemsTreeView.selectionModel().currentChanged.connect(self.showTreeItemDetailedInfo)
        self.detailedInfoModel.valueChangeFailed.connect(self.itemDataChangeFailed)
        # todo delete
        self.comboBox.currentTextChanged.connect(self.toggleTheme)
        self.actionLight.triggered.connect(self.setLightTheme)
        self.actionDark.triggered.connect(self.setDarkTheme)
        self.detailInfoTreeView.expanded.connect(self.hideDetailInfoParentRow)
        self.detailInfoTreeView.collapsed.connect(self.showDetailInfoRowVal)

    def hideDetailInfoParentRow(self, index):
        if self.detailedInfoModel.objByIndex(index).children():
            self.detailedInfoModel.hideRowVal(index)

    def showDetailInfoRowVal(self, index):
        self.detailedInfoModel.showRowVal(index)

    def showTreeItemDetailedInfo(self, treeItem):
        main_obj = treeItem.data(Qt.UserRole)
        self.pathLabel.setText(self.getTreeItemPath(treeItem))
        self.detailedInfoModel = DetailedInfoTable(mainObj=main_obj, objStore=self.objStore)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), treeItem.data(Qt.DisplayRole))
        self.detailInfoTreeView.setModel(self.detailedInfoModel)
        # self.detailInfoTreeView.expandAll()
        self.detailInfoTreeView.setItemDelegate(QComboBoxEnumDelegate())
        self.detailedInfoModel.valueChangeFailed.connect(self.itemDataChangeFailed)

    def getTreeItemPath(self, treeItem):
        path = treeItem.data(Qt.DisplayRole)
        while treeItem.parent().isValid():
            treeItem = treeItem.parent()
            path = f"{treeItem.data(Qt.DisplayRole)}/{path}"
        return path

    def itemDataChangeFailed(self, msg):
        self.statusbar.showMessage(msg)

    def setLightTheme(self):
        self.toggleTheme("light")

    def setDarkTheme(self):
        self.toggleTheme("dark")

    def toggleTheme(self, theme):
        if theme == "dark":
            self.toggleStylesheet(DARK_THEME_PATH)
        elif theme == "light":
            self.toggleStylesheet(LIGHT_THEME_PATH)

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