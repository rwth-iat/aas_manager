from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QModelIndex
from PyQt5.QtGui import QMouseEvent, QKeySequence
from PyQt5.QtWidgets import QTreeView, QTabWidget, QWidget, QLineEdit, QLabel, QMenu, QSizePolicy, \
    QFrame, QAbstractScrollArea, QGridLayout, QVBoxLayout, QMessageBox, QDialog
from PyQt5.Qt import Qt

from aas_editor.dialogs import AddDescriptionDialog
from aas_editor.qcomboboxenumdelegate import QComboBoxEnumDelegate
from aas_editor.qt_models import OBJECT_ROLE, NAME_ROLE, DetailedInfoTable, PACKAGE_ROLE, \
    ATTRIBUTE_COLUMN, DetailedInfoItem
from aas_editor.settings import ATTR_COLUMN_WIDTH
from aas_editor.util import getTreeItemPath


class TreeView(QTreeView):
    wheelClicked = pyqtSignal(['QModelIndex'])

    def __init__(self, parent=None):
        super(TreeView, self).__init__(parent)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        super(TreeView, self).mousePressEvent(e)
        if e.button() == Qt.MiddleButton:
            self.wheelClicked.emit(self.currentIndex())


class TabWidget(QTabWidget):
    def __init__(self, parent: QWidget = None, packTreeView: TreeView = None):
        super(TabWidget, self).__init__(parent)
        self.packTreeView = packTreeView
        self.buildHandlers()

    def buildHandlers(self):
        self.tabCloseRequested.connect(self.removeTab)

    def openPackItemTab(self, packItem, setCurrent=True):
        tabName = packItem.data(NAME_ROLE)

        if not self.isTabOpen(tabName, setCurrent):
            tab = Tab(packItem, parent=self)
            self.addTab(tab, tabName)
            if setCurrent:
                self.setCurrentWidget(tab)

    def isTabOpen(self, tabName, setCurrent=True):
        for index in range(self.count()):
            if self.tabText(index) == tabName:
                tab = self.widget(index)
                self.setCurrentWidget(tab)
                return True

    def removeTab(self, index):
        widget = self.widget(index)
        if widget is not None:
            widget.deleteLater()
        super(TabWidget, self).removeTab(index)


class Tab(QWidget):
    def __init__(self, packItem=QModelIndex(), parent: TabWidget = None):
        super(Tab, self).__init__(parent)
        self.pathLabel = QLineEdit(getTreeItemPath(packItem), self)
        self.pathLabel.setReadOnly(True)
        self.descrLabel = QLabel(self)
        self.detailInfoMenu = QMenu(self)
        self._initTreeView(packItem)
        self._initLayout()
        self.buildHandlers()

    def _initTreeView(self, packItem):
        self.detailInfoTreeView = TreeView(self)
        self.detailInfoTreeView.setExpandsOnDoubleClick(False)
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
        self.detailInfoTreeView.expanded.connect(self.detailedInfoModel.hideRowVal)
        self.detailInfoTreeView.collapsed.connect(self.detailedInfoModel.showRowVal)
        self.detailedInfoModel.valueChangeFailed.connect(self.itemDataChangeFailed)
        self.detailInfoTreeView.selectionModel().currentChanged.connect(self.showDetailInfoItemDoc)
        self.detailInfoTreeView.selectionModel().currentChanged.connect(self.updateDetailInfoItemMenu)
        self.detailInfoTreeView.customContextMenuRequested.connect(self.openDetailInfoItemMenu)
        self.detailInfoTreeView.setItemDelegate(QComboBoxEnumDelegate())
        self.detailInfoTreeView.doubleClicked.connect(self.openRefTab)
        self.detailInfoTreeView.wheelClicked.connect(lambda refItem: self.openRefTab(refItem, setCurrent=False))

    def openRefTab(self, detailInfoItem: QModelIndex, setCurrent=True):
        item = self.detailedInfoModel.objByIndex(detailInfoItem)
        if item.isLink:
            obj = item.obj.resolve(item.package.objStore)
            linkedPackItem = self.parent().parent().packTreeView.model().findItemByObj(obj)
            self.parent().parent().openPackItemTab(linkedPackItem, setCurrent)

    def showDetailInfoItemDoc(self, detailInfoItem: QModelIndex):
        self.descrLabel.setText(detailInfoItem.data(Qt.ToolTipRole))

    def itemDataChangeFailed(self, msg):
        QMessageBox.critical(self, "Error", msg)  # todo find out how to pass app, not Tab

    def updateDetailInfoItemMenu(self, index):
        self.detailInfoMenu.clear()
        # print("b ", self.actions())
        # for a in self.actions():
        #     self.removeAction(a)
        # print(self.actions())

        if index.data(NAME_ROLE) == "description":
            act = self.detailInfoMenu.addAction(self.tr("Add description"),
                                                lambda i=index: self.addDescrWithDialog(i),
                                                QKeySequence.New)
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