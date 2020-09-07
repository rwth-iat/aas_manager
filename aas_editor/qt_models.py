import typing
import collections

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QObject, QVariant, QModelIndex, QAbstractItemModel, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from aas.model.aas import *
from aas.model.base import *
from aas.model.concept import *
from aas.model.submodel import *

COLUMNS_IN_DETAILED_INFO = ("attribute", "value")
ATTRIBUTE_COLUMN = 0
VALUE_COLUMN = 1

STRING_ATTRS = ("id", "id_short", "category", "version", "revision")

# todo delete
IMPLEMENTED_ATTRS = STRING_ATTRS + ("administration", "identification", "kind", "entity_type",)
SUBMODEL_ATTRS = ("asset_identification_model", "bill_of_material")
PACKAGE_ATTRS_NOT_IN_DETAILED_INFO = ("shells", "assets", "submodels", "concept_descriptions")

# ATTRS_NOT_IN_DETAILED_INFO = ("namespace_element_sets", "submodel", "submodel_element", "asset", "parent") + SUBMODEL_ATTRS + PACKAGE_ATTRS_NOT_IN_DETAILED_INFO
# ATTRS_IN_LEFT_TREEVIEW = ("shells", "assets", "submodels", "concept_descriptions", "submodel", "submodel_element", "concept_dictionary", "asset")
ATTRS_NOT_IN_DETAILED_INFO = ("namespace_element_sets", "parent") + PACKAGE_ATTRS_NOT_IN_DETAILED_INFO
ATTRS_IN_LEFT_TREEVIEW = PACKAGE_ATTRS_NOT_IN_DETAILED_INFO

VALUE_ATTRS = ("value", "in_output_variable", "input_variable", "output_variable", "first", "second")
ATTR_ORDER = ("id_short", "category",) + VALUE_ATTRS + ("kind", "entity_type", "description", "administration", "identification",)


def name_is_special(method_name):
    "Returns true if the method name starts with underscore"
    return method_name.startswith('_')


def get_attrs(obj, excludeSpecial=True, excludeCallable=True):
    attrs = dir(obj)
    if excludeSpecial:
        attrs[:] = [attr for attr in attrs if not name_is_special(attr)]
    if excludeCallable:
        attrs[:] = [attr for attr in attrs if not callable(getattr(obj, attr))]
    return attrs


def attr_order(attr):
    if attr in ATTR_ORDER:
        return ATTR_ORDER.index(attr)
    return 1000


def get_attrs4detail_info(obj, excludeSpecial=True, excludeCallable=True):
    attrs = get_attrs(obj, excludeSpecial, excludeCallable)
    attrs[:] = [attr for attr in attrs if attr not in ATTRS_NOT_IN_DETAILED_INFO]
    attrs.sort(key=attr_order)
    return attrs


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

    def addItem(self, item, parentIndex):
        self.beginInsertRows(parentIndex, self.rowCount(parentIndex), self.rowCount(parentIndex))
        item.setParent(self.objByIndex(parentIndex))
        self.endInsertRows()

    def objByIndex(self, index):
        if not index.isValid():
            return self._rootItem
        return index.internalPointer()

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
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

    def rowCount(self, parent):
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

    def __init__(self, mainObj=None, objStore=None):
        super(DetailedInfoTable, self).__init__(COLUMNS_IN_DETAILED_INFO)
        self.mainObj = mainObj
        self.objStore = objStore
        if self.mainObj:
            self.fillTable()

    def fillTable(self):
        attrs = get_attrs4detail_info(self.mainObj)
        print(f"Attributes to add to detailed info: {attrs}")

        for attr in attrs:
            print(f"Add to detailed info attribute {attr}")
            obj = getattr(self.mainObj, attr)
            item = DetailedInfoItem(obj, attr, masterObj=self.mainObj, objStore=self.objStore)
            self.addItem(item, QModelIndex())

    def hideRowVal(self, index):
        self.objByIndex(index).dataValueHidden = True

    def showRowVal(self, index):
        self.objByIndex(index).dataValueHidden = False

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
                f"{self.objByIndex(index).objectName} couldn't be changed to {value}")
        except (ValueError, AttributeError) as e:
            self.dataChanged.emit(index, index)
            self.valueChangeFailed.emit(
                f"Error occured while setting {self.objByIndex(index).objName}: {e}")
        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags

        return self.objByIndex(index).flags(index.column())


class StandardItem(QObject):
    def __init__(self, obj, name=None, parent=None):
        super().__init__(parent)
        self.obj = obj
        self.objName = name

    @property
    def objectName(self):
        if hasattr(self.obj, "id_short"):
            return self.obj.id_short
        elif self.objName:
            return self.objName
        else:
            return self.obj.__class__.__name__

    def row(self):
        if self.parent():
            return self.parent().children().index(self)
        else:
            return 0


class DetailedInfoItem(StandardItem):
    def __init__(self, obj, name, parent=None, masterObj=None, objStore=None):
        super().__init__(obj, name, parent)
        self.dataValueHidden = False
        self.masterObj = masterObj
        self.objStore = objStore
        if masterObj or parent:
            self.parentObj = self.masterObj if self.masterObj else self.parent().obj
            self.populate()

    def data(self, role, column=VALUE_COLUMN):
        # if role == Qt.ToolTipRole:
        #     return inspect.getdoc(self.obj)
        if role == Qt.BackgroundRole:
            color = QColor(132, 185, 225)
            if self.masterObj:
                if self.row() % 2:
                    color.setAlpha(150)
                else:
                    color.setAlpha(110)
            else:
                if self.row() is 0:
                    color.setAlpha(260 - self.parent().data(Qt.BackgroundRole).alpha())
                else:
                    color.setAlpha(260 - self.parent().children()[self.row() - 1].data(
                        Qt.BackgroundRole).alpha())
            return color
        if column == VALUE_COLUMN:
            if role == Qt.DisplayRole and not self.dataValueHidden:
                return str(self.obj)
            elif role == Qt.EditRole:
                return self.obj
        elif column == ATTRIBUTE_COLUMN:
            if role == Qt.DisplayRole:
                return self.objName
            elif role == Qt.EditRole:
                return self.objName
            elif role == Qt.FontRole and not isinstance(self.parentObj, dict):
                font = QFont()
                font.setBold(True)
                return font
        return QVariant()

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
        if isinstance(self.obj, (str, int, float, bool, Enum)):
            return
        elif type(self.obj) is AASReference:
            obj = self.obj
            # if self.resolveRefs:
            if True:
                try:
                    obj = self.obj.resolve(self.objStore)
                except (KeyError, NotImplementedError) as e:
                    print(e)
            for sub_item_attr in get_attrs4detail_info(obj):
                DetailedInfoItem(obj=getattr(obj, sub_item_attr), name=sub_item_attr, parent=self,
                                 objStore=self.objStore)
        elif isinstance(self.obj, dict):
            for sub_item_attr, sub_item_obj in self.obj.items():
                DetailedInfoItem(sub_item_obj, sub_item_attr, self, objStore=self.objStore)
        elif isinstance(self.obj, (set, list, tuple, NamespaceSet)):
            for i, sub_item_obj in enumerate(self.obj):
                DetailedInfoItem(sub_item_obj, f"item {i}", self, objStore=self.objStore)
        else:
            for sub_item_attr in get_attrs4detail_info(self.obj):
                DetailedInfoItem(getattr(self.obj, sub_item_attr), sub_item_attr, self,
                                 objStore=self.objStore)


class AasTreeViewItem(StandardItem):
    def __init__(self, obj, parent=None, objStore=None, objName=None):
        # todo fix
        # super().__init__(obj, obj.id_short, parent)
        super().__init__(obj, objName, parent)
        self.objStore = objStore
        self.preffered_lang = "en-us"
        self.populate()

    def set_language(self, lang):
        self.preffered_lang = lang

    def data(self, role):
        if role == Qt.DisplayRole:
            return self.objectName
        if role == Qt.ToolTipRole and hasattr(self.obj, "description"):
            return str(self.obj.description.get(self.preffered_lang))
        if role == Qt.StatusTipRole and hasattr(self.obj, "description"):
            return str(self.obj.description.get(self.preffered_lang))
        if role == Qt.UserRole:
            return self.obj
        return QtCore.QVariant()

    def populate(self):
        # todo fix
        try:
            # package and standard populate
            for attr in ATTRS_IN_LEFT_TREEVIEW:
                if hasattr(self.obj, attr):
                    attr_obj = getattr(self.obj, attr)
                    parent = AasTreeViewItem(obj=attr_obj, parent=self, objStore=self.objStore, objName=attr)
                    if isinstance(attr_obj, collections.Iterable):
                        for i in attr_obj:
                            AasTreeViewItem(obj=i, parent=parent, objStore=self.objStore)
        except (KeyError, NotImplementedError) as e:
            print(e)


class Package:
    def __init__(self, objStore):
        self.shells = []
        self.assets = []
        self.submodels = []
        self.concept_descriptions = []
        self.add_items(objStore)

    def add_items(self, objStore):
        for item in objStore:
            if isinstance(item, AssetAdministrationShell):
                self.shells.append(item)
            elif isinstance(item, Asset):
                self.assets.append(item)
            elif isinstance(item, Submodel):
                self.submodels.append(item)
            elif isinstance(item, ConceptDescription):
                self.concept_descriptions.append(item)

    @property
    def num_of_shells(self):
        return len(self.shells)

    @property
    def num_of_assets(self):
        return len(self.assets)

    @property
    def num_of_submodels(self):
        return len(self.submodels)

    @property
    def num_of_concept_descriptions(self):
        return len(self.concept_descriptions)

# ToDo logs insteads of prints
