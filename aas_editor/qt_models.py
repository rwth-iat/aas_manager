# pyuic5 aas_editor/mainwindow_base.ui -o aas_editor/design.py
import collections
import typing

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QObject, QVariant, QModelIndex, QAbstractItemModel, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from aas.model.aas import *
from aas.model.base import *
from aas.model.concept import *
from aas.model.provider import *
from aas.model.submodel import *

from .settings import ATTRS_IN_PACKAGE_TREEVIEW
from .util import getAttrs4detailInfo, simplifyInfo, getDescription, getAttrDoc, getAttrs

PACKAGE_ROLE = 1001
NAME_ROLE = 1002
OBJECT_ROLE = 1003

TYPES_NOT_TO_POPULATE = (str, int, float, bool, Enum,)  # '+ TYPES_IN_ONE_ROW

COLUMNS_IN_DETAILED_INFO = ("attribute", "value")
ATTRIBUTE_COLUMN = 0
VALUE_COLUMN = 1

STRING_ATTRS = ("id", "id_short", "category", "version", "revision")
SUBMODEL_ATTRS = ("asset_identification_model", "bill_of_material")


class Package:
    def __init__(self, objStore: DictObjectStore = None, name=""):
        self.name = name
        self.objStore = objStore if objStore else DictObjectStore()

    @property
    def shells(self):
        for obj in self.objStore:
            if isinstance(obj, AssetAdministrationShell):
                yield obj

    @property
    def assets(self):
        for obj in self.objStore:
            if isinstance(obj, Asset):
                yield obj

    @property
    def submodels(self):
        for obj in self.objStore:
            if isinstance(obj, Submodel):
                yield obj

    @property
    def concept_descriptions(self):
        for obj in self.objStore:
            if isinstance(obj, ConceptDescription):
                yield obj

    @property
    def others(self):
        for obj in self.objStore:
            if not isinstance(obj, (AssetAdministrationShell, Asset, Submodel, ConceptDescription)):
                yield obj

    def add(self, obj):
        self.objStore.add(obj)

    @property
    def numOfShells(self):
        return len(tuple(self.shells))

    @property
    def numOfAssets(self):
        return len(tuple(self.assets))

    @property
    def numOfSubmodels(self):
        return len(tuple(self.submodels))

    @property
    def numOfConceptDescriptions(self):
        return len(tuple(self.concept_descriptions))

# class TreeItem(DetailedInfoItem):
#     def __init__(self, obj, name, parent=None):
#         super().__init__(obj, name, parent)
#         self.has_children = True
#         self.children_fetched = False
#
#     def append_child(self, item):
#         item.parent_item = self
#         self.child_items.append(item)
#
#     def insert_children(self, idx, items):
#         self.child_items[idx:idx] = items
#         for item in items:
#             item.parent_item = self
#
#     def child(self, row):
#         return self.child_items[row]
#
#     def child_count(self):
#         return len(self.child_items)
#
#     def data(self, role):
#         return QVariant()

class StandardTable(QAbstractItemModel):
    def __init__(self, columns=("Item",)):
        super(StandardTable, self).__init__()
        self._rootItem = DetailedInfoItem(self, "")
        self._columns = columns

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        return self.objByIndex(index).data(role)

    def addItem(self, item, parent: QModelIndex = QModelIndex()):
        if isinstance(parent.parent().data(OBJECT_ROLE), Package):
            pack: Package = self.objByIndex(parent.parent()).data(OBJECT_ROLE)
            pack.add(item.data(OBJECT_ROLE))
        elif isinstance(parent.data(OBJECT_ROLE), dict):
            dictionary = self.objByIndex(parent).data(OBJECT_ROLE)
            key = item.data(NAME_ROLE)
            value = item.data(OBJECT_ROLE)
            dictionary[key] = value
        self.beginInsertRows(parent, self.rowCount(parent), self.rowCount(parent))
        item.setParent(self.objByIndex(parent))
        self.endInsertRows()
        return self.index(item.row(), 0, parent)

    def objByIndex(self, index):
        if not index.isValid():
            return self._rootItem
        return index.internalPointer()

    def findItemByObj(self, obj):
        for item in self.iterItems():
            print("Name:", item.data(NAME_ROLE))
            if item.data(OBJECT_ROLE) == obj:
                return item

    def iterItems(self, parent: QModelIndex = QModelIndex()):
        def recurse(parent):
            for row in range(self.rowCount(parent)):
                childIndex = self.index(row, 0, parent)
                yield childIndex
                child = self.objByIndex(childIndex)
                if child.children():
                    yield from recurse(childIndex)

        yield from recurse(parent)

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        parentObj = self.objByIndex(parent)
        return self.createIndex(row, column, parentObj.children()[row])

    def parent(self, child: QModelIndex) -> QModelIndex:
        childObj = self.objByIndex(child)
        parentObj = childObj.parent()
        if parentObj == self._rootItem:
            return QModelIndex()
        grandParentObj = parentObj.parent()
        row = grandParentObj.children().index(parentObj)
        return self.createIndex(row, 0, parentObj)

    def rowCount(self, parent=QModelIndex()):
        return len(self.objByIndex(parent).children())

    def columnCount(self, parent=None):
        return len(self._columns)

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._columns[section]

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable


class DetailedInfoTable(StandardTable):
    valueChangeFailed = pyqtSignal(['QString'])

    def __init__(self, mainObj=None, package: Package = None):
        super(DetailedInfoTable, self).__init__(COLUMNS_IN_DETAILED_INFO)
        self.mainObj = mainObj
        self.package = package
        if self.mainObj:
            self.fillTable()

    def fillTable(self):
        attrs = getAttrs4detailInfo(self.mainObj)
        print(f"Attributes to add to detailed info: {attrs}")

        for attr in attrs:
            print(f"Add to detailed info attribute {attr}")
            obj = getattr(self.mainObj, attr)
            item = DetailedInfoItem(obj, attr, masterObj=self.mainObj, package=self.package)
            self.addItem(item, QModelIndex())

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        return self.objByIndex(index).data(role, index.column())

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if not index.isValid():
            return QVariant()
        try:
            if self.objByIndex(index).setData(value, role, index.column()):
                return True
            self.valueChangeFailed.emit(
                f"{self.objByIndex(index).objectName} could not be changed to {value}")
        except (ValueError, AttributeError) as e:
            self.dataChanged.emit(index, index)
            self.valueChangeFailed.emit(
                f"Error occurred while setting {self.objByIndex(index).objName}: {e}")
        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags

        return self.objByIndex(index).flags(index.column())

    def replaceItemObj(self, obj, index: QModelIndex = QModelIndex()):
        self.objByIndex(index).setData(obj, Qt.EditRole)
        self.objByIndex(index).populate()

        rows=self.rowCount()
        cols=self.columnCount()
        top_left=self.index(0,0)
        bot_right=self.index(rows-1, cols-1)
        self.dataChanged.emit(top_left, bot_right)


class StandardItem(QObject):
    def __init__(self, obj, name=None, parent=None):
        super().__init__(parent)
        self.obj = obj
        self.objName = name

    @property
    def objectName(self):
        if self.objName:
            return self.objName
        elif hasattr(self.obj, "id_short") and self.obj.id_short:
            return self.obj.id_short
        else:
            return self.obj.__class__.__name__

    def row(self):
        if self.parent():
            return self.parent().children().index(self)
        else:
            return 0


class DetailedInfoItem(StandardItem):
    def __init__(self, obj, name, parent=None, masterObj=None, package: Package = None):
        super().__init__(obj, name, parent)
        self.masterObj = masterObj
        self.package = package
        self.isLink = self._isLink()
        if masterObj or parent:
            self.parentObj = self.masterObj if self.masterObj else self.parent().obj
            self.populate()

    def _isLink(self):
        if self.package and isinstance(self.obj, AASReference):
            try:
                self.obj.resolve(self.package.objStore)
                return True
            except (KeyError, NotImplementedError) as e:
                print(e)
        return False

    def data(self, role, column=VALUE_COLUMN):
        if role == Qt.ToolTipRole:
            return getAttrDoc(self.objName, self.parentObj.__init__.__doc__)
        if role == NAME_ROLE:
            return self.objectName
        if role == OBJECT_ROLE:
            return self.obj
        if role == PACKAGE_ROLE:
            return self.package
        if role == Qt.BackgroundRole:
            return self._getBgColor()
        if role == Qt.ForegroundRole:
            return self._getFgColor(column)
        if role == Qt.FontRole:
            return self._getFont(column)
        if role == Qt.DisplayRole:
            if column == ATTRIBUTE_COLUMN:
                return self.objName
            if column == VALUE_COLUMN:
                return simplifyInfo(self.obj, self.objectName)
        if role == Qt.EditRole:
            if column == ATTRIBUTE_COLUMN:
                return self.objName
            if column == VALUE_COLUMN:
                return self.obj
        return QVariant()

    def _getBgColor(self):
        color = QColor(132, 185, 225)
        if self.masterObj:
            if self.row() % 2:
                color.setAlpha(150)
            else:
                color.setAlpha(110)
        else:
            if self.row() == 0:
                color.setAlpha(260 - self.parent().data(Qt.BackgroundRole).alpha())
            else:
                color.setAlpha(
                    260 - self.parent().children()[self.row() - 1].data(Qt.BackgroundRole).alpha())
        return color

    def _getFgColor(self, column):
        if column == VALUE_COLUMN:
            if self.isLink:
                return QColor(26, 13, 171)
        return QVariant()

    def _getFont(self, column):
        font = QFont()
        if column == ATTRIBUTE_COLUMN:
            if not isinstance(self.parentObj, dict):
                font.setBold(True)
            return font
        if column == VALUE_COLUMN:
            if self.isLink:
                font.setUnderline(True)
            return font
        return QVariant()

    def setParent(self, a0: 'QObject') -> None:
        super().setParent(a0)
        if not self.masterObj:
            self.parentObj = a0.obj

    def setData(self, value, role, column=VALUE_COLUMN):
        if role == Qt.EditRole:
            valueToSet = self.defineValue(value)
            if column == VALUE_COLUMN:
                if isinstance(self.parentObj, list):
                    self.parentObj[self.row()] = valueToSet
                    self.obj = self.parentObj[self.row()]
                elif isinstance(self.parentObj, dict):
                    self.parentObj[self.objName] = valueToSet
                    self.obj = self.parentObj[self.objName]
                else:
                    setattr(self.parentObj, self.objName, valueToSet)
                    self.obj = getattr(self.parentObj, self.objName)
                if self.obj == valueToSet:
                    return True
            elif column == ATTRIBUTE_COLUMN:
                if isinstance(self.parentObj, dict):
                    self.parentObj[valueToSet] = self.parentObj.pop(self.objName)
                    self.objName = valueToSet
                    return True
        return False

    def defineValue(self, value):
        print(value, type(value))
        if self.objName in STRING_ATTRS:
            return None if value == "None" else str(value)
        if not isinstance(value, str):
            return value
        return value

    def flags(self, column):
        if column == ATTRIBUTE_COLUMN and not isinstance(self.parentObj, dict):
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

        if self.children():
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def populate(self):
        if isinstance(self.obj, TYPES_NOT_TO_POPULATE):
            return
        elif type(self.obj) is AASReference:
            obj = self.obj
            for sub_item_attr in getAttrs4detailInfo(obj):
                DetailedInfoItem(obj=getattr(obj, sub_item_attr), name=sub_item_attr, parent=self,
                                 package=self.package)
        elif isinstance(self.obj, dict):
            for sub_item_attr, sub_item_obj in self.obj.items():
                DetailedInfoItem(sub_item_obj, sub_item_attr, self, package=self.package)
        elif isinstance(self.obj, (set, list, tuple, NamespaceSet)):
            for i, sub_item_obj in enumerate(self.obj):
                DetailedInfoItem(sub_item_obj, f"{sub_item_obj.__class__.__name__} {i}", self,
                                 package=self.package)
        else:
            for sub_item_attr in getAttrs4detailInfo(self.obj):
                DetailedInfoItem(getattr(self.obj, sub_item_attr), sub_item_attr, self,
                                 package=self.package)


class PackTreeViewItem(StandardItem):
    def __init__(self, obj, parent=None, objName=None):
        super().__init__(obj, objName, parent)
        if parent:
            self.package = parent.data(PACKAGE_ROLE)
        else:
            self.package = obj
        self.populate()

    def data(self, role):
        if role == NAME_ROLE:
            return self.objectName
        if role == OBJECT_ROLE:
            return self.obj
        if role == PACKAGE_ROLE:
            return self.package
        if role == Qt.DisplayRole:
            return self.objectName
        if role == Qt.ToolTipRole and hasattr(self.obj, "description"):
            return getDescription(self.obj.description)
        return QtCore.QVariant()

    def setParent(self, a0: 'QObject') -> None:
        super().setParent(a0)
        self.package = a0.data(PACKAGE_ROLE)

    def populate(self):
        # todo make populate of PackTreeViewItem smarter (may be with typing check)
        try:
            for attr in ATTRS_IN_PACKAGE_TREEVIEW:
                if hasattr(self.obj, attr):
                    attr_obj = getattr(self.obj, attr)
                    parent = PackTreeViewItem(obj=attr_obj, parent=self, objName=attr)
                    if isinstance(attr_obj, collections.Iterable):
                        for i in attr_obj:
                            PackTreeViewItem(obj=i, parent=parent)
            for attr in ("submodel_element",):
                if hasattr(self.obj, attr):
                    attr_obj = getattr(self.obj, attr)
                    if attr_obj:
                        for i in attr_obj:
                            PackTreeViewItem(obj=i, parent=self)

        except (KeyError, NotImplementedError) as e:
            print(e)
