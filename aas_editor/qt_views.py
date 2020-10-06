from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QModelIndex, QItemSelectionModel
from PyQt5.QtGui import QMouseEvent, QKeySequence, QIcon, QKeyEvent
from PyQt5.QtWidgets import QTreeView, QTabWidget, QWidget, QLineEdit, QLabel, QMenu, QSizePolicy, \
    QFrame, QAbstractScrollArea, QGridLayout, QVBoxLayout, QMessageBox, QDialog, QShortcut, \
    QApplication, QAction, QAbstractItemView
from PyQt5.Qt import Qt
from aas.model import AssetAdministrationShell, Asset, Submodel, SubmodelElement

from aas_editor.dialogs import AddDescriptionDialog, AddAdministrationDialog, AddDialog, \
    AddAASRefDialog, AddObjDialog, ChooseFromDialog
from aas_editor.qcomboboxenumdelegate import QComboBoxEnumDelegate
from aas_editor.qt_models import OBJECT_ROLE, NAME_ROLE, DetailedInfoTable, PACKAGE_ROLE, \
    ATTRIBUTE_COLUMN, DetailedInfoItem, VALUE_COLUMN, PackTreeViewItem
from aas_editor.settings import ATTR_COLUMN_WIDTH
from aas_editor.util import getTreeItemPath, inheritors


class TreeView(QTreeView):
    wheelClicked = pyqtSignal(['QModelIndex'])
    openInCurrTabClicked = pyqtSignal(['QModelIndex'])
    openInNewTabClicked = pyqtSignal(['QModelIndex'])
    openInBackgroundTabClicked = pyqtSignal(['QModelIndex'])

    def __init__(self, parent=None):
        super(TreeView, self).__init__(parent)
        self.attrsMenu = QMenu(self)
        self._initMenu()
        self.customContextMenuRequested.connect(self.openDetailInfoItemMenu)

    def _initMenu(self):
        self.attrsMenu.addSeparator()
        self.collapseAct = self.attrsMenu.addAction("C&ollapse", lambda: self.collapse(self.currentIndex()))
        self.expandAct = self.attrsMenu.addAction("E&xpand", lambda: self.expand(self.currentIndex()))
        self.collapseAllAct = self.attrsMenu.addAction("Co&llapse all", self.collapseAll)
        self.expandAllAct = self.attrsMenu.addAction("Ex&pand all", self.expandAll)
        self.attrsMenu.addSeparator()

    def openDetailInfoItemMenu(self, point):
        self.attrsMenu.exec_(self.viewport().mapToGlobal(point))

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.MiddleButton:
            self.wheelClicked.emit(self.indexAt(e.pos()))
        else:
            super(TreeView, self).mousePressEvent(e)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Return:
        # we captured the Enter key press, now we need to move to the next row
            nextRow = self.currentIndex().row() + 1
            if nextRow+1 > self.model().rowCount(self.currentIndex().parent()):
                # we are all the way down, we can 't go any further
                nextRow = nextRow - 1
            if self.state() == QAbstractItemView.EditingState:
                # if we are editing, confirm and move to the row below
                nextIndex = self.currentIndex().siblingAtRow(nextRow)
                self.setCurrentIndex(nextIndex)
                self.selectionModel().select(nextIndex, QItemSelectionModel.ClearAndSelect)
            else:
                # if we're not editing, check if editable and start editing or expand/collapse
                index2edit = self.currentIndex().siblingAtColumn(VALUE_COLUMN)
                if index2edit.flags() & Qt.ItemIsEditable:
                    self.edit(index2edit)
                else:
                    index2fold = self.currentIndex().siblingAtColumn(0)
                    if self.isExpanded(index2fold):
                        self.collapse(index2fold)
                    else:
                        self.expand(index2fold)
        else:
            # any other key was pressed, inform base
            super(TreeView, self).keyPressEvent(event)

    def collapse(self, index: QtCore.QModelIndex) -> None:
        newIndex = index.siblingAtColumn(0)
        super(TreeView, self).collapse(newIndex)

    def expand(self, index: QtCore.QModelIndex) -> None:
        newIndex = index.siblingAtColumn(0)
        super(TreeView, self).expand(newIndex)


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
            self._updateMenu()

    def _updateMenu(self):
        menuActions = self.attrsMenu.actions()

        self.addAct = QAction("&Add")
        self.addAct.setStatusTip("Add item to selected")
        self.addAct.setEnabled(True)
        self.attrsMenu.insertAction(menuActions[0], self.addAct)

        self.addAct.triggered.connect(self.addHandler)

        self.openInCurrTabAct = self.attrsMenu.addAction("Open in current ta&b", lambda: self.openInCurrTabClicked.emit(self.currentIndex()))
        self.openInNewTabAct = self.attrsMenu.addAction("Open in new &tab", lambda: self.openInNewTabClicked.emit(self.currentIndex()))
        self.openInBackgroundAct = self.attrsMenu.addAction("Open in &background tab", lambda: self.openInBackgroundTabClicked.emit(self.currentIndex()))

    def addHandler(self):
        index = self.currentIndex()
        attribute = index.data(NAME_ROLE)
        if attribute == "shells":
            self.addItemWithDialog(index, AssetAdministrationShell)
        elif attribute == "assets":
            self.addItemWithDialog(index, Asset)
        elif attribute == "submodels":
            self.addItemWithDialog(index, Submodel)
        elif isinstance(index.data(OBJECT_ROLE), Submodel):
            classesToChoose = inheritors(SubmodelElement)
            dialog = ChooseFromDialog(classesToChoose, "Choose submodel element type", self)
            if dialog.exec_() == QDialog.Accepted:
                kls = dialog.getObj2add()
                self.addItemWithDialog(index, kls)

    def addItemWithDialog(self, index, objType):
        dialog = AddObjDialog(objType, self)
        if dialog.exec_() == QDialog.Accepted:
            obj = dialog.getObj2add()
            item = self.model().addItem(PackTreeViewItem(obj=obj), index)
            self.setFocus()
            self.setCurrentIndex(item)
        else:
            print("Item adding cancelled")
        dialog.deleteLater()


class AttrsTreeView(TreeView):
    def __init__(self, parent):
        super(AttrsTreeView, self).__init__(parent)
        self._updateMenu()
        self.buildHandlers()
        self.packTreeView: PackTreeView = PackTreeView.instance()

    def _updateMenu(self):
        menuActions = self.attrsMenu.actions()

        self.editAct = QAction("&Edit")
        self.editAct.setStatusTip("Edit selected item")
        self.editAct.setDisabled(True)
        self.attrsMenu.insertAction(menuActions[0], self.editAct)

        self.addAct = QAction("&Add")
        self.addAct.setStatusTip("Add item to selected")
        self.addAct.setDisabled(True)
        self.attrsMenu.insertAction(self.editAct, self.addAct)

        self.addAct.triggered.connect(self.addHandler)
        self.editAct.triggered.connect(lambda: self.edit(self.currentIndex()))

        self.openInCurrTabAct = self.attrsMenu.addAction("Open in current ta&b", lambda: self.openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN), newTab=False))
        self.openInNewTabAct = self.attrsMenu.addAction("Open in new &tab", lambda: self.openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN)))
        self.openInBackgroundAct = self.attrsMenu.addAction("Open in &background tab", lambda: self.openRef(self.currentIndex().siblingAtColumn(VALUE_COLUMN), setCurrent=False))


    def buildHandlers(self):
        self.setItemDelegate(QComboBoxEnumDelegate())
        self.clicked.connect(self.openRef)
        self.wheelClicked.connect(lambda refItem: self.openRef(refItem, newTab=True, setCurrent=False))

    def buildHandlersForNewItem(self):
        self.model().valueChangeFailed.connect(self.parent().itemDataChangeFailed)
        self.selectionModel().currentChanged.connect(self.updateDetailInfoItemMenu)

    def updateDetailInfoItemMenu(self, index: QModelIndex):
        self.addAct.setDisabled(True)
        self.addAct.setText("Add")
        if index.data(NAME_ROLE) == "description":
            self.addAct.setEnabled(True)
            self.addAct.setText("Add description")
        elif index.data(NAME_ROLE) == "administration" and not index.data(OBJECT_ROLE):
            self.addAct.setEnabled(True)
            self.addAct.setText("Add administration")
        elif index.data(NAME_ROLE) in ("derived_from", "asset", "asset_identification_model", "bill_of_material", "semantic_id", "value_id", "first", "second") and not index.data(OBJECT_ROLE):
            self.addAct.setEnabled(True)
            self.addAct.setText("Add AASReference")

        self.editAct.setDisabled(True)
        if index.parent().isValid() and isinstance(index.parent().data(OBJECT_ROLE), dict):
                indexEdit = index
        else:
            indexEdit = index.siblingAtColumn(VALUE_COLUMN)
        if indexEdit.flags() & Qt.ItemIsEditable:
            self.setCurrentIndex(indexEdit)
            self.editAct.setEnabled(True)

        self.openInCurrTabAct.setDisabled(True)
        self.openInBackgroundAct.setDisabled(True)
        self.openInNewTabAct.setDisabled(True)

        if self.model().objByIndex(index).isLink:
            self.openInCurrTabAct.setEnabled(True)
            self.openInBackgroundAct.setEnabled(True)
            self.openInNewTabAct.setEnabled(True)

    def addHandler(self):
        index = self.currentIndex()
        attribute = index.data(NAME_ROLE)
        if attribute == "description":
            self.addDescrWithDialog(index)
        elif attribute == "administration":
            self.addAdministrationWithDialog(index)
        elif attribute in ("derived_from", "asset", "asset_identification_model", "bill_of_material", "semantic_id", "value_id", "first", "second"):
            self.addAASRefWithDialog(index)

    def newPackItem(self, packItem):
        self._initTreeView(packItem)
        self.buildHandlersForNewItem()

    def addDescrWithDialog(self, index):
        dialog = AddDescriptionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            descrUpdateDict = dialog.getObj2add()
            for lang, descr in descrUpdateDict.items():
                self.model().addItem(DetailedInfoItem(obj=descr, name=lang), index)
        else:
            print("Asset adding cancelled")
        dialog.deleteLater()

    def addAdministrationWithDialog(self, index):
        dialog = AddAdministrationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            administration = dialog.getObj2add()
            self.model().replaceItemObj(administration, index)
        else:
            print("Administration adding cancelled")
        dialog.deleteLater()

    def addAASRefWithDialog(self, index):
        dialog = AddAASRefDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            ref = dialog.getObj2add()
            self.model().replaceItemObj(ref, index)
        else:
            print("Reference adding cancelled")
        dialog.deleteLater()

    def openRef(self, detailInfoItem: QModelIndex, newTab=True, setCurrent=True): # todo reimplement search func findItemByObj
        item = self.model().objByIndex(detailInfoItem)
        if detailInfoItem.column() == VALUE_COLUMN and item.isLink:
            obj = item.obj.resolve(item.package.objStore)
            linkedPackItem = self.packTreeView.model().findItemByObj(obj)
            if newTab and setCurrent:
                self.openInNewTabClicked.emit(linkedPackItem)
            elif newTab and not setCurrent:
                self.openInBackgroundTabClicked.emit(linkedPackItem)
            else:
                self.openInCurrTabClicked.emit(linkedPackItem)

    def _initTreeView(self, packItem):
        self.setExpandsOnDoubleClick(False)
        self.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(429, 0))
        self.setBaseSize(QtCore.QSize(429, 555))
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Sunken)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.setObjectName("attrsTreeView")

        attrsModel = DetailedInfoTable(mainObj=packItem.data(OBJECT_ROLE),
                                       package=packItem.data(PACKAGE_ROLE))
        self.setModel(attrsModel)
        self.setColumnWidth(ATTRIBUTE_COLUMN, ATTR_COLUMN_WIDTH)
        self.setItemDelegate(QComboBoxEnumDelegate())


class TabWidget(QTabWidget):
    # signal for changing current item in packet treeview
    currItemChanged = pyqtSignal(['QModelIndex'])

    def __init__(self, parent: QWidget = None):
        super(TabWidget, self).__init__(parent)
        self.nextTabAct = QAction("Next tab", self)
        self.backAct = QAction(QIcon.fromTheme("go-previous"), "Back", self)
        self.forwardAct = QAction(QIcon.fromTheme("go-next"), "Forward", self)
        self._setupActions()
        self.buildHandlers()

    def _setupActions(self):
        self.backAct.setDisabled(True)
        self.backAct.setShortcut(QKeySequence.Back)
        self.backAct.setToolTip(f"Go back ({self.backAct.shortcut().toString()})")

        self.forwardAct.setDisabled(True)
        self.forwardAct.setShortcut(QKeySequence.Forward)
        self.forwardAct.setToolTip(f"Go forward ({self.backAct.shortcut().toString()})")

        self.nextTabAct.setShortcut(QKeySequence.NextChild)

    def buildHandlers(self):
        self.tabCloseRequested.connect(self.removeTab)
        self.currentChanged.connect(self._currentTabChanged)
        self.currItemChanged.connect(self._updateActions)
        self.backAct.triggered.connect(lambda: self.currentWidget().openPrevItem())
        self.forwardAct.triggered.connect(lambda: self.currentWidget().openNextItem())
        self.nextTabAct.triggered.connect(self._switch2nextTab)

    def tabInserted(self, index):
        super(TabWidget, self).tabInserted(index)
        tab: Tab = self.widget(index)
        tab.objectNameChanged.connect(lambda text: self.setTabText(self.indexOf(tab), text))
        tab.currItemChanged.connect(lambda packItem: self._handleCurrTabItemChanged(tab, packItem))
        tab.attrsTreeView.openInCurrTabClicked.connect(self.openItem)
        tab.attrsTreeView.openInNewTabClicked.connect(self.openItemInNewTab)
        tab.attrsTreeView.openInBackgroundTabClicked.connect(self.openItemInBackgroundTab)

    def _handleCurrTabItemChanged(self, tab, packItem):
        if tab == self.currentWidget():
            self.currItemChanged.emit(packItem)

    def _currentTabChanged(self, index):
        if index >= 0:
            self.currItemChanged.emit(self.widget(index).packItem)
        else:
            self.currItemChanged.emit(QModelIndex())

    def _switch2nextTab(self):
        nextIndex = self.currentIndex() + 1
        nextIndexPossible = (self.count() <= nextIndex)
        if nextIndexPossible:
            self.setCurrentIndex(nextIndex)
        else:
            self.setCurrentIndex(0)

    def _updateActions(self):
        tab: Tab = self.currentWidget()
        if tab:
            self.forwardAct.setEnabled(True) if tab.nextItems else self.forwardAct.setDisabled(True)
            self.backAct.setEnabled(True) if tab.prevItems else self.backAct.setDisabled(True)

    def openItem(self, packItem: QModelIndex = QModelIndex()) -> int:
        if not self.count():
            return self.openItemInNewTab(packItem)
        else:
            self.currentWidget().openItem(packItem)
            return self.currentIndex()

    def openItemInNewTab(self, packItem: QModelIndex, afterCurrent: bool = True) -> int:
        tab = Tab(packItem, parent=self)
        if afterCurrent:
            tabIndex = self.insertTab(self.currentIndex()+1, tab, tab.objectName)
        else:
            tabIndex = self.addTab(tab, tab.objectName)
        self.setCurrentWidget(tab)
        self.currItemChanged.emit(packItem)
        return tabIndex

    def openItemInBackgroundTab(self, packItem: QModelIndex) -> int:
        tab = Tab(packItem, parent=self)
        tabIndex = self.insertTab(self.currentIndex()+1, tab, tab.objectName)
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
    currItemChanged = pyqtSignal(['QModelIndex'])

    def __init__(self, packItem=QModelIndex(), parent: TabWidget = None):
        super(Tab, self).__init__(parent)

        self.pathLine: QLineEdit = QLineEdit(self)
        self.pathLine.setReadOnly(True)

        self.descrLabel = QLabel(self)
        self.descrLabel.setWordWrap(True)
        self.descrLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.attrsTreeView = AttrsTreeView(self)

        self.packItem: QModelIndex = QModelIndex()
        self.prevItems = []
        self.nextItems = []
        self.openItem(packItem)

        self._initLayout()

    @property
    def objectName(self) -> str:
        return self.packItem.data(NAME_ROLE)

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
        self.attrsTreeView.newPackItem(packItem)
        self.attrsTreeView.selectionModel().currentChanged.connect(self.showDetailInfoItemDoc)
        self.packItem = packItem
        self.pathLine.setText(getTreeItemPath(packItem))
        self.objectNameChanged.emit(self.objectName)
        self.currItemChanged.emit(self.packItem)

    def showDetailInfoItemDoc(self, detailInfoItem: QModelIndex):
        self.descrLabel.setText(detailInfoItem.data(Qt.ToolTipRole))

    def itemDataChangeFailed(self, msg):
        QMessageBox.critical(self, "Error", msg)

    def _initLayout(self):
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.addWidget(self.descrLabel, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.attrsTreeView, 0, 0, 1, 1)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.addWidget(self.pathLine)
        self.verticalLayout.addLayout(self.gridLayout)