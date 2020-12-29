from enum import Enum
from typing import Any, Iterable, Union, AbstractSet, List

from PyQt5.QtCore import QAbstractItemModel, QVariant, QModelIndex, Qt, QItemSelection, QSize
from PyQt5.QtGui import QFont

from aas_editor.models import DetailedInfoItem, StandardItem, PackTreeViewItem
from aas_editor.package import Package
from aas_editor.settings.app_settings import NAME_ROLE, OBJECT_ROLE, ATTRIBUTE_COLUMN, \
    VALUE_COLUMN, NOT_GIVEN, \
    PACKAGE_ROLE, PACK_ITEM_ROLE, DEFAULT_FONT, ADD_ITEM_ROLE, CLEAR_ROW_ROLE, \
    DATA_CHANGE_FAILED_ROLE, IS_LINK_ROLE, LINK_BLUE, NEW_GREEN, CHANGED_BLUE, RED, TYPE_COLUMN, \
    TYPE_CHECK_ROLE, TYPE_ROLE

from aas_editor.utils.util_classes import DictItem, ClassesInfo


class StandardTable(QAbstractItemModel):
    defaultFont = QFont(DEFAULT_FONT)

    def __init__(self, columns=("Item",), rootItem: StandardItem = None):
        super(StandardTable, self).__init__()
        self._rootItem = rootItem if rootItem else DetailedInfoItem(None) # FIXME
        self._columns = columns
        self.lastErrorMsg = ""

    def index(self, row: int, column: int = 0, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        parentObj = self.objByIndex(parent)
        return self.createIndex(row, column, parentObj.children()[row])

    def parent(self, child: QModelIndex) -> QModelIndex:
        if not child.isValid():
            return QModelIndex()

        childObj = self.objByIndex(child)
        parentObj = childObj.parent()

        if parentObj == self._rootItem or not parentObj:
            return QModelIndex()

        grandParentObj = parentObj.parent()
        row = grandParentObj.children().index(parentObj)
        return self.createIndex(row, 0, parentObj)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.objByIndex(parent).children())

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._columns)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> Any:
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._columns[section]

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags

        if (index.column() != VALUE_COLUMN
            and not isinstance(index.data(OBJECT_ROLE), DictItem)) \
                or self.hasChildren(index):
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

        # FIXME check if other types are also editable
        if isinstance(index.data(OBJECT_ROLE),
                      (DictItem, Enum, bool, int, float, str, bytes, type(None), dict, list, AbstractSet)):
            return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def hasChildren(self, parent: QModelIndex = ...) -> bool:
        return True if self.rowCount(parent) else False

    def objByIndex(self, index: QModelIndex):
        if not index.isValid():
            return self._rootItem
        return index.internalPointer()

    def iterItems(self, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        def recurse(parent: QModelIndex):
            for row in range(self.rowCount(parent)):
                childIndex = self.index(row, 0, parent)
                yield childIndex
                child = self.objByIndex(childIndex)
                if child.children():
                    yield from recurse(childIndex)
        yield from recurse(parent)

    def match(self, start: QModelIndex, role: int, value: Any, hits: int = ...,
              flags: Union[Qt.MatchFlags, Qt.MatchFlag] = ...) -> List[QModelIndex]:
        kwargs = {}
        if hits is not ...:
            kwargs["hits"] = hits
        if flags is not ...:
            kwargs["flags"] = flags

        if role == OBJECT_ROLE and hits != 0:
            res = []
            for item in self.iterItems(start):
                print("match for:", item.data(NAME_ROLE))
                try:
                    if (item.data(OBJECT_ROLE) is value) or (item.data(OBJECT_ROLE) == value):
                        res.append(item)
                except AttributeError:
                    continue
                if hits == len(res):
                    break
            return res
        elif role == TYPE_ROLE and hits != 0:
            res = []
            for item in self.iterItems(start):
                print("match for:", item.data(NAME_ROLE))
                try:
                    if issubclass(value, item.data(TYPE_ROLE)):
                        res.append(item)
                except AttributeError:
                    continue
                if hits == len(res):
                    break
            return res
        elif role == Qt.DisplayRole and hits != 0:
            res = []
            for item in self.iterItems(start):
                print("match for:", item.data(NAME_ROLE))
                try:
                    if value == item.data(Qt.DisplayRole):
                        res.append(item)
                except AttributeError:
                    continue
                if hits == len(res):
                    break
            return res
        else:
            return super(StandardTable, self).match(start, role, value, **kwargs)

    def addItem(self, obj: Union[Package, 'SubmodelElement', Iterable],
                parent: QModelIndex = QModelIndex()):
        parent = parent.siblingAtColumn(0)
        parentItem = self.objByIndex(parent)
        parentObj = parentItem.data(OBJECT_ROLE)
        parentObjCls = type(parentObj)
        parentName = parent.data(NAME_ROLE)

        kwargs = {
            "obj": obj,
            "parent": parentItem,
        }
        if isinstance(obj, Package):
            kwargs["parent"] = self._rootItem
            kwargs["new"] = False
            itemTyp = PackTreeViewItem
        elif parentName in Package.addableAttrs():
            package: Package = parent.data(PACKAGE_ROLE)
            package.add(obj)
            itemTyp = PackTreeViewItem
        elif ClassesInfo.changedParentObject(parentObjCls):
            parentObj = getattr(parentObj, ClassesInfo.changedParentObject(parentObjCls))
            parentObj.add(obj)
            itemTyp = PackTreeViewItem
        elif isinstance(parentObj, AbstractSet):
            parentObj.add(obj)
            itemTyp = DetailedInfoItem
        elif isinstance(parentObj, list):
            parentObj.append(obj)
            itemTyp = DetailedInfoItem
        elif isinstance(parentObj, dict):
            parentObj[obj.key] = obj.value
            itemTyp = DetailedInfoItem
        else:
            raise AttributeError(
                f"Object couldn't be added: parent obj type is not appendable: {type(parentObj)}")
        self.beginInsertRows(parent, 0, 0)
        item = itemTyp(**kwargs)
        self.endInsertRows()
        # self.insertRow(max(self.rowCount(parent)-1, 0), parent)
        return self.index(item.row(), 0, parent)

    def insertRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        self.beginInsertRows(parent, row, row + count - 1)
        self.endInsertRows()
        return True

    def update(self, index: QModelIndex):
        if not index.isValid():
            return QVariant()
        if self.hasChildren(index):
            self.beginRemoveRows(index, 0, max(self.rowCount(index)-1, 0))
            self.removeRows(0, self.rowCount(index), index)
            self.endRemoveRows()
            self.rowsRemoved.emit(index, 0, max(self.rowCount(index)-1, 0))
            self.dataChanged.emit(index, index.child(self.rowCount(index) - 1,
                                                     self.columnCount(index) - 1))

        self.objByIndex(index).populate()
        if self.hasChildren(index):
            self.beginInsertRows(index, 0, max(self.rowCount(index)-1, 0))
            self.endInsertRows()
            self.rowsInserted.emit(index, 0, max(self.rowCount(index)-1, 0))
            self.dataChanged.emit(index, index.child(self.rowCount(index)-1, self.columnCount(index)-1))
        else:
            self.dataChanged.emit(index, index)
        return True

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if role == Qt.BackgroundRole:
            return self._getBgColor(index)
        if role == Qt.ForegroundRole:
            return self._getFgColor(index)
        if role == Qt.FontRole:
            return self._getFont(index)
        if role == Qt.SizeHintRole:
            fontSize = self.defaultFont.pointSize()
            return QSize(-1, fontSize*1.7)
        if role == Qt.TextAlignmentRole:
            return Qt.AlignLeft | Qt.AlignBottom
        if role == DATA_CHANGE_FAILED_ROLE:
            return self.lastErrorMsg
        else:
            item = self.objByIndex(index)
            return item.data(role, index.column())

    def _getBgColor(self, index: QModelIndex):
        return self.objByIndex(index).data(Qt.BackgroundRole)

    def _getFgColor(self, index: QModelIndex):
        column = index.column()
        # color fg in red if obj type and typehint don't fit
        if column == TYPE_COLUMN and not index.data(TYPE_CHECK_ROLE):
            return RED
        elif column == VALUE_COLUMN and index.data(IS_LINK_ROLE):
            return LINK_BLUE
        elif column == ATTRIBUTE_COLUMN:
            if self.objByIndex(index).new:
                return NEW_GREEN
            elif self.objByIndex(index).changed:
                return CHANGED_BLUE
        return QVariant()

    def _getFont(self, index: QModelIndex) -> QFont:
        font = QFont(self.defaultFont)
        if index.column() == VALUE_COLUMN and index.data(IS_LINK_ROLE):
            font.setUnderline(True)
        return font

    def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        if not index.isValid() and role not in (Qt.FontRole, ADD_ITEM_ROLE):
            return QVariant()
        elif role == Qt.BackgroundRole:
            item = self.objByIndex(index)
            res = item.setData(value, role, index.column())
            self.dataChanged.emit(index, index)
            return res
        elif role == Qt.FontRole:
            if isinstance(value, QFont):
                font = QFont(value)
                self.defaultFont.setPointSize(font.pointSize())
                self.dataChanged.emit(self.index(0), self.index(self.rowCount()))
                return True
            return False
        elif role == ADD_ITEM_ROLE:
            try:
                self.addItem(value, index)
                return True
            except Exception as e:
                self.lastErrorMsg = f"Error occurred while adding item to {index.data(NAME_ROLE)}: {e}"
                print(self.lastErrorMsg)
                self.dataChanged.emit(index, index, [DATA_CHANGE_FAILED_ROLE])
                return False
        elif role == CLEAR_ROW_ROLE:
            try:
                self.clearRow(index.row(), index.parent(), value)
                return True
            except Exception as e:
                self.lastErrorMsg = f"{index.data(NAME_ROLE)} could not be deleted or set to default: {e}"
                self.dataChanged.emit(index, index, [DATA_CHANGE_FAILED_ROLE])
                return False
        elif role == Qt.EditRole:
            try:
                value = None if str(value) == "None" else value
                item = self.objByIndex(index)
                if isinstance(index.parent().data(OBJECT_ROLE), list):
                    parentList: List = item.parentObj
                    parentList[parentList.index(item.obj)] = value
                    item.obj = value
                elif isinstance(index.parent().data(OBJECT_ROLE), AbstractSet):
                    parentSet: AbstractSet = item.parentObj
                    parentSet.remove(item.obj)
                    parentSet.add(value)
                    item.obj = value
                elif isinstance(index.data(OBJECT_ROLE), DictItem):
                    if index.column() == VALUE_COLUMN:
                        item.obj = DictItem(item.obj.key, value)
                    elif index.column() == ATTRIBUTE_COLUMN:
                        item.parentObj.pop(item.obj.key)
                        item.obj = DictItem(value, item.obj.value)
                    item.parentObj.update([item.obj])
                else:
                    setattr(item.parentObj, item.objName, value)
                    item.obj = getattr(item.parentObj, item.objName)
                self.setChanged(index)
                self.update(index)
                return True
            except Exception as e:
                self.lastErrorMsg = f"Error occurred while setting {self.objByIndex(index).objectName}: {e}"
                self.dataChanged.emit(index, index, [DATA_CHANGE_FAILED_ROLE])
            return False

    def setChanged(self, topLeft: QModelIndex, bottomRight: QModelIndex = None):
        """Set the item and all parents as changed"""
        bottomRight = topLeft if bottomRight is None else bottomRight
        if topLeft.isValid() and bottomRight.isValid():
            selection = QItemSelection(topLeft, bottomRight)
            for index in selection.indexes():
                self.objByIndex(index).changed = True
                if index.parent().isValid():
                    self.setChanged(index.parent())
                else:
                    packItem: QModelIndex = index.data(PACK_ITEM_ROLE)
                    if packItem and packItem.isValid():
                        packItem.model().dataChanged.emit(packItem, packItem)

    def removeRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        parentItem = self.objByIndex(parent)

        self.beginRemoveRows(parent, row, row+count-1)
        for n in range(count):
            child = parentItem.children()[row]
            child.setParent(None)
            # child.deleteLater()
        self.endRemoveRows()
        # self.dataChanged.emit(parent, parent)
        # self.rowsRemoved.emit(parent, row, row-1+count)
        return True

    def clearRows(self, row: int, count: int,
                  parent: QModelIndex = ..., defaultVal=NOT_GIVEN) -> bool:
        """Delete rows if they are children of Iterable else set to Default"""
        parentItem = self.objByIndex(parent)
        parentObj = parentItem.data(OBJECT_ROLE)

        # if parentObj is Submodel and the parentObj is not rootItem
        # set submodel_element as parentObj
        if parent.isValid():
            try:
                parentAttr = ClassesInfo.changedParentObject(type(parentObj)) #FIXME delete if Namespace.discard() works
                parentObj = getattr(parentObj, parentAttr)
            except AttributeError:
                pass

        for currRow in range(row+count-1, row-1, -1):
            child = parentItem.children()[currRow]
            if isinstance(parentObj, list):
                parentObj.pop[currRow]
                self.removeRow(currRow, parent)
            elif isinstance(parentObj, dict):
                parentObj.pop(child.objectName)
                self.removeRow(currRow, parent)
            elif isinstance(parentObj, AbstractSet):
                parentObj.discard(child.obj)
                self.removeRow(currRow, parent)
            else:
                if not defaultVal == NOT_GIVEN:
                    self.setData(self.index(currRow, 0, parent), defaultVal, Qt.EditRole)
                else:
                    raise TypeError(
                        f"Unknown parent object type: "
                        f"object could not be deleted or set to default: "
                        f"{type(parentObj)}")
        return True

    def clearRow(self, row: int, parent: QModelIndex = ..., defaultVal=NOT_GIVEN) -> bool:
        """Delete row if it is child of Iterable else set to Default"""
        return self.clearRows(row, 1, parent, defaultVal)
