from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QModelIndex
from PyQt5.QtGui import QMouseEvent, QKeySequence, QIcon
from PyQt5.QtWidgets import QTreeView, QTabWidget, QWidget, QLineEdit, QLabel, QMenu, QSizePolicy, \
    QFrame, QAbstractScrollArea, QGridLayout, QVBoxLayout, QMessageBox, QDialog, QShortcut, \
    QApplication, QAction
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
    # signal for changing current item in packet treeview
    currItemChanged = pyqtSignal(['QModelIndex'])

    def __init__(self, parent: QWidget = None):
        super(TabWidget, self).__init__(parent)
        # redefine shortcut here so that this works from everywhere
        self.shortcutNextTab = QShortcut(QKeySequence(QKeySequence.NextChild), self)
        self.backAct = QAction(QIcon.fromTheme("go-previous"), "Back", self)
        self.forwardAct = QAction(QIcon.fromTheme("go-next"), "Forward", self)
        self._setupActions()
        self.buildHandlers()

    def currentWidget(self) -> 'Tab':
        return super(TabWidget, self).currentWidget()

    def _setupActions(self):
        self.backAct.setDisabled(True)
        self.backAct.setShortcut(QKeySequence.Back)
        self.backAct.setToolTip(f"Go back ({self.backAct.shortcut().toString()})")

        self.forwardAct.setDisabled(True)
        self.forwardAct.setShortcut(QKeySequence.Forward)
        self.forwardAct.setToolTip(f"Go forward ({self.backAct.shortcut().toString()})")

    def buildHandlers(self):
        self.tabCloseRequested.connect(self.removeTab)
        self.currentChanged.connect(self._currentChanged)
        self.currItemChanged.connect(self._updateActions)
        self.backAct.triggered.connect(lambda: self.currentWidget().openPrevItem())
        self.forwardAct.triggered.connect(lambda: self.currentWidget().openNextItem())
        self.shortcutNextTab.activated.connect(self._switch2nextTab)

    def _currentChanged(self, index):
        if index >= 0:
            self.currItemChanged.emit(self.widget(index).packItem)
        else:
            self.currItemChanged.emit(QModelIndex())

    def _switch2nextTab(self):
        nextIndex = self.currentIndex() + 1
        nextIndexPossible = (self.count() <= nextIndex)
        self.setCurrentIndex(nextIndex) if nextIndexPossible else self.setCurrentIndex(0)

    def _updateActions(self):
        tab: Tab = self.currentWidget()
        if tab:
            self.forwardAct.setEnabled(True) if tab.nextItems else self.forwardAct.setDisabled(True)
            self.backAct.setEnabled(True) if tab.prevItems else self.backAct.setDisabled(True)

    def openItem(self, packItem: QModelIndex = QModelIndex(), newTab: bool = True, setCurrent: bool = True) -> int:
        if newTab or not self.count():
            return self.addItemTab(packItem, setCurrent)
        else:
            self.currentWidget().openItem(packItem)
            return self.currentIndex()

    def addItemTab(self, packItem: QModelIndex, setCurrent: bool = True) -> int:
        tab = Tab(packItem, parent=self)
        tabIndex = self.addTab(tab, tab.objectName)
        if setCurrent:
            self.setCurrentWidget(tab)
            self.currItemChanged.emit(packItem)
        return tabIndex

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


class Tab(QWidget):
    def __init__(self, packItem=QModelIndex(), parent: TabWidget = None):
        super(Tab, self).__init__(parent)
        # self.app: 'EditorApp' = self.window()
        self.tabWidget: TabWidget = self.window().tabWidget
        self.packTreeView: PackTreeView = PackTreeView.instance()
        self.pathLine: QLineEdit = QLineEdit(self)
        self.pathLine.setReadOnly(True)
        self.descrLabel = QLabel(self)
        self.attrsTreeView = TreeView(self)
        self.detailedInfoModel = DetailedInfoTable()
        self.packItem: QModelIndex = QModelIndex()
        self.prevItems = []
        self.nextItems = []
        self.openItem(packItem)
        self.detailInfoMenu = QMenu(self)
        self._initMenu()
        self._initLayout()
        self.buildHandlers()


    def _initMenu(self):
        self.addAct = self.detailInfoMenu.addAction(
            "&Add", lambda: self.addDescrWithDialog(self.attrsTreeView.currentIndex()))
        self.addAct.setDisabled(True)
        self.detailInfoMenu.addAction(
            "&Edit", lambda: self.attrsTreeView.edit(self.attrsTreeView.currentIndex()))
        self.addAct.setDisabled(True)
        self.detailInfoMenu.addSeparator()
        self.detailInfoMenu.addAction(
            "&Collapse",
            lambda: self.attrsTreeView.collapse(self.attrsTreeView.currentIndex()))
        self.detailInfoMenu.addAction(
            "E&xpand",
            lambda: self.attrsTreeView.expand(self.attrsTreeView.currentIndex()))
        self.detailInfoMenu.addAction(
            "Co&llapse all",
            self.attrsTreeView.collapseAll)
        self.detailInfoMenu.addAction(
            "Ex&pand all",
            self.attrsTreeView.expandAll)
        self.detailInfoMenu.addSeparator()
        self.detailInfoMenu.addAction(
            "Open in new &tab",
            lambda: self.openRef(self.attrsTreeView.currentIndex(), newTab=True, setCurrent=True))
        self.detailInfoMenu.addAction(
            "Open in &background tab",
            lambda: self.openRef(self.attrsTreeView.currentIndex(), newTab=True, setCurrent=False))

    def updateDetailInfoItemMenu(self, index):
        pass
        # self.detailInfoMenu.clear()
        # # print("b ", self.actions())
        # # for a in self.actions():
        # #     self.removeAction(a)
        # # print(self.actions())
        #
        # if index.data(NAME_ROLE) == "description":
        #     act = self.detailInfoMenu.addAction(self.tr("Add description"),
        #                                         lambda i=index: self.addDescrWithDialog(i),
        #                                         QKeySequence.New)
        #     self.addAction(act)

    @property
    def objectName(self) -> str:
        return self.packItem.data(NAME_ROLE)

    def isCurrent(self) -> bool:
        return self.tabWidget.currentIndex() == self.tabWidget.indexOf(self)

    def buildHandlers(self):
        self.attrsTreeView.customContextMenuRequested.connect(self.openDetailInfoItemMenu)
        self.attrsTreeView.setItemDelegate(QComboBoxEnumDelegate())
        self.attrsTreeView.clicked.connect(self.openRef)
        self.attrsTreeView.wheelClicked.connect(lambda refItem: self.openRef(refItem, newTab=True, setCurrent=False))

    def buildHandlersForNewItem(self):
        self.detailedInfoModel.valueChangeFailed.connect(self.itemDataChangeFailed)
        self.attrsTreeView.selectionModel().currentChanged.connect(self.showDetailInfoItemDoc)
        self.attrsTreeView.selectionModel().currentChanged.connect(self.updateDetailInfoItemMenu)

    def openItem(self, packItem):
        if not packItem == self.packItem:
            self.nextItems.clear()
            if self.packItem.isValid():
                self.prevItems.append(self.packItem)
            self._openItem(packItem)

    def openPrevItem(self):
        if self.prevItems:
            prevItem = self.prevItems.pop()
            self.nextItems.append(self.packItem)
            self._openItem(prevItem)

    def openNextItem(self):
        if self.nextItems:
            nextItem = self.nextItems.pop()
            self.prevItems.append(self.packItem)
            self._openItem(nextItem)

    def _openItem(self, packItem):
        self._initTreeView(packItem)
        self.packItem = packItem
        self.pathLine.setText(getTreeItemPath(packItem))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self), self.objectName)
        self.buildHandlersForNewItem()
        if self.isCurrent():
            self.tabWidget.currItemChanged.emit(self.packItem)

    def openRef(self, detailInfoItem: QModelIndex, newTab=False, setCurrent=True): # todo reimplement search func findItemByObj
        item = self.detailedInfoModel.objByIndex(detailInfoItem)
        if detailInfoItem.column() == VALUE_COLUMN and item.isLink:
            obj = item.obj.resolve(item.package.objStore)
            linkedPackItem = self.packTreeView.model().findItemByObj(obj)
            self.tabWidget.openItem(linkedPackItem, newTab, setCurrent)

    def showDetailInfoItemDoc(self, detailInfoItem: QModelIndex):
        self.descrLabel.setText(detailInfoItem.data(Qt.ToolTipRole))

    def itemDataChangeFailed(self, msg):
        QMessageBox.critical(self, "Error", msg)

    def openDetailInfoItemMenu(self, point):
        self.detailInfoMenu.exec_(self.attrsTreeView.viewport().mapToGlobal(point))

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
        self.attrsTreeView.setExpandsOnDoubleClick(False)
        self.attrsTreeView.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.attrsTreeView.sizePolicy().hasHeightForWidth())
        self.attrsTreeView.setSizePolicy(sizePolicy)
        self.attrsTreeView.setMinimumSize(QtCore.QSize(429, 0))
        self.attrsTreeView.setBaseSize(QtCore.QSize(429, 555))
        self.attrsTreeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.attrsTreeView.setFrameShape(QFrame.StyledPanel)
        self.attrsTreeView.setFrameShadow(QFrame.Sunken)
        self.attrsTreeView.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.attrsTreeView.setObjectName("attrsTreeView")

        self.detailedInfoModel = DetailedInfoTable(mainObj=packItem.data(OBJECT_ROLE),
                                                   package=packItem.data(PACKAGE_ROLE))
        self.attrsTreeView.setModel(self.detailedInfoModel)
        self.attrsTreeView.setColumnWidth(ATTRIBUTE_COLUMN, ATTR_COLUMN_WIDTH)
        self.attrsTreeView.setItemDelegate(QComboBoxEnumDelegate())

    def _initLayout(self):
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.addWidget(self.descrLabel, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.attrsTreeView, 0, 0, 1, 1)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.addWidget(self.pathLine)
        self.verticalLayout.addLayout(self.gridLayout)