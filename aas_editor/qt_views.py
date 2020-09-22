from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QModelIndex
from PyQt5.QtGui import QMouseEvent, QKeySequence
from PyQt5.QtWidgets import QTreeView, QTabWidget, QWidget, QLineEdit, QLabel, QMenu, QSizePolicy, \
    QFrame, QAbstractScrollArea, QGridLayout, QVBoxLayout, QMessageBox, QDialog, QShortcut, \
    QApplication
from PyQt5.Qt import Qt

from aas_editor.dialogs import AddDescriptionDialog
from aas_editor.qcomboboxenumdelegate import QComboBoxEnumDelegate
from aas_editor.qt_models import OBJECT_ROLE, NAME_ROLE, DetailedInfoTable, PACKAGE_ROLE, \
    ATTRIBUTE_COLUMN, DetailedInfoItem, VALUE_COLUMN
from aas_editor.settings import ATTR_COLUMN_WIDTH
from aas_editor.util import getTreeItemPath


class TreeView(QTreeView):
    wheelClicked = pyqtSignal(['QModelIndex'])

    def __init__(self, parent=None):
        super(TreeView, self).__init__(parent)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.MiddleButton:
            self.wheelClicked.emit(self.indexAt(e.pos()))
        else:
            super(TreeView, self).mousePressEvent(e)


class PackTreeView(TreeView):
    """Singleton class"""
    __instance = None

    @staticmethod
    def instance() -> 'PackTreeView':
        """Instance access method"""
        if PackTreeView.__instance is None:
            PackTreeView()
        return PackTreeView.__instance

    def __init__(self, parent=None):
        if PackTreeView.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            super(PackTreeView, self).__init__(parent)
            PackTreeView.__instance = self


class TabWidget(QTabWidget):
    def __init__(self, parent: QWidget = None):
        super(TabWidget, self).__init__(parent)
        self.packTreeView = PackTreeView.instance()
        self.app = self.window()
        # redefine shortcut here so that this works from everywhere
        self.shortcutNextTab = QShortcut(QKeySequence(QKeySequence.NextChild), self)
        self.buildHandlers()

    def buildHandlers(self):
        self.tabCloseRequested.connect(self.removeTab)
        self.currentChanged.connect(self._currTabChanged)
        self.shortcutNextTab.activated.connect(lambda: self.setCurrentIndex((self.count()//(self.currentIndex()+2)*(self.currentIndex()+1))))

    def _currTabChanged(self, index):
        currTab = self.widget(index)
        currTab.checkActions()
        if self.count():
            self.packTreeView.setCurrentIndex(self.widget(index).packItem)
        else:
            self.packTreeView.setCurrentIndex(QModelIndex())

    def openNextItem(self):
        self.currentWidget().openNextItem()

    def openPrevItem(self):
        self.currentWidget().openPrevItem()

    def openPackItemTab(self, packItem: QModelIndex, newTab: bool = True, setCurrent: bool = True) -> int:
        if newTab or not self.count():
            return self._addPackItemTab(packItem, setCurrent)
        else:
            currTab = self.currentWidget()
            currTab.openNewItem(packItem)
            return self.currentIndex()

    def _addPackItemTab(self, packItem: QModelIndex, setCurrent: bool = True) -> int:
        tab = Tab(packItem, parent=self)
        tabIndex = self.addTab(tab, tab.objectName)
        if setCurrent:
            self.setCurrentWidget(tab)
            self.packTreeView.setCurrentIndex(packItem)
        return tabIndex

    def isTabOpen(self, tabName):
        for index in range(self.count()):
            if self.tabText(index) == tabName:
                return True
        return False

    def setCurrentTab(self, tabName):
        for index in range(self.count()):
            if self.tabText(index) == tabName:
                tab = self.widget(index)
                self.setCurrentWidget(tab)
                return True
        return False

    def removeTab(self, index):
        widget = self.widget(index)
        if widget is not None:
            widget.deleteLater()
        super(TabWidget, self).removeTab(index)


class Tab(QWidget):# todo change current if change tab
    def __init__(self, packItem=QModelIndex(), parent: TabWidget = None):
        super(Tab, self).__init__(parent)
        self.app: 'EditorApp' = self.window()
        self.tabWidget: TabWidget = self.app.tabWidget
        self.packTreeView: PackTreeView = PackTreeView.instance()
        self.pathLabel = QLineEdit(self)
        self.pathLabel.setReadOnly(True)
        self.descrLabel = QLabel(self)
        self.detailInfoMenu = QMenu(self)
        self.detailInfoTreeView = TreeView(self)
        self.packItem: QModelIndex = None
        self.prevItems = []
        self.nextItems = []
        self.openNewItem(packItem)
        self._initLayout()
        self.buildHandlers()

    @property
    def objectName(self) -> str:
        return self.packItem.data(NAME_ROLE)

    def isCurrent(self) -> bool:
        return self.tabWidget.currentIndex() == self.tabWidget.indexOf(self)

    def buildHandlers(self):
        self.detailInfoTreeView.expanded.connect(self.detailedInfoModel.hideRowVal)
        self.detailInfoTreeView.collapsed.connect(self.detailedInfoModel.showRowVal)
        self.detailInfoTreeView.customContextMenuRequested.connect(self.openDetailInfoItemMenu)
        self.detailInfoTreeView.setItemDelegate(QComboBoxEnumDelegate())
        self.detailInfoTreeView.clicked.connect(self.openRefTab)
        self.detailInfoTreeView.wheelClicked.connect(lambda refItem: self.openRefTab(refItem, newTab=True, setCurrent=False))

    def buildHandlersForNewItem(self):
        self.detailedInfoModel.valueChangeFailed.connect(self.itemDataChangeFailed) # todo find out what if new item is opened
        self.detailInfoTreeView.selectionModel().currentChanged.connect(self.showDetailInfoItemDoc)
        self.detailInfoTreeView.selectionModel().currentChanged.connect(self.updateDetailInfoItemMenu)

    def openNewItem(self, packItem):
        if not packItem == self.packItem:
            if self .packItem and self.packItem.isValid():
                self.prevItems.append(self.packItem)
            self.nextItems.clear()
            self._openNewItem(packItem)

    def openPrevItem(self):
        if self.prevItems:
            prevItem = self.prevItems.pop()
            self.nextItems.append(self.packItem)
            self._openNewItem(prevItem)

    def openNextItem(self):
        if self.nextItems:
            nextItem = self.nextItems.pop()
            self.prevItems.append(self.packItem)
            self._openNewItem(nextItem)

    def _openNewItem(self, packItem):
        self._initTreeView(packItem)
        self.packItem = packItem
        self.pathLabel.setText(getTreeItemPath(packItem))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self), self.objectName)
        self.buildHandlersForNewItem()
        if self.isCurrent():
            self.checkActions()

    def checkActions(self):
        # self.app.forwardAct.setEnabled(True) if self.nextItems else False
        # self.app.backwardAct.setEnabled(True) if self.prevItems else False
        if self.nextItems:
            self.app.forwardAct.setEnabled(True)
        else:
            self.app.forwardAct.setDisabled(True)

        if self.prevItems:
            self.app.backwardAct.setEnabled(True)
        else:
            self.app.backwardAct.setDisabled(True)

    def openRefTab(self, detailInfoItem: QModelIndex, newTab=False, setCurrent=True):
        item = self.detailedInfoModel.objByIndex(detailInfoItem)
        if detailInfoItem.column() == VALUE_COLUMN and item.isLink:
            obj = item.obj.resolve(item.package.objStore)
            linkedPackItem = self.tabWidget.packTreeView.model().findItemByObj(obj)
            self.tabWidget.openPackItemTab(linkedPackItem, newTab, setCurrent)

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

    def _initTreeView(self, packItem):
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