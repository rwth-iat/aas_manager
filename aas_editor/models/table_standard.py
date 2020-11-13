from enum import Enum
from typing import Any, Iterable, Union, AbstractSet

from PyQt5.QtCore import QAbstractItemModel, QVariant, QModelIndex, Qt, pyqtSignal, QItemSelection, \
    QSize
from PyQt5.QtGui import QFont

from aas_editor.models import Package, DetailedInfoItem, StandardItem, PackTreeViewItem
from aas_editor.settings import NAME_ROLE, OBJECT_ROLE, ATTRIBUTE_COLUMN, VALUE_COLUMN, NOT_GIVEN, \
    PACKAGE_ROLE, PACK_ITEM_ROLE, PACKAGE_ATTRS, DEFAULT_FONT

from aas.model import Submodel, SubmodelElement


class StandardTable(QAbstractItemModel):
    valueChangeFailed = pyqtSignal(['QString'])
    defaultFont = QFont(DEFAULT_FONT)

    def __init__(self, columns=("Item",), rootItem: StandardItem = None):
        super(StandardTable, self).__init__()
        self._rootItem = rootItem if rootItem else DetailedInfoItem(None, "") # FIXME
        self._columns = columns
        self.dataChanged.connect(self.setChanged)

    def index(self, row: int, column: int = 0, parent: QModelIndex = QModelIndex()) -> QModelIndex:
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

        if (index.column() == ATTRIBUTE_COLUMN
            and not isinstance(index.parent().data(OBJECT_ROLE), dict)) \
                or self.hasChildren(index):
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

        # FIXME check if other types are also editable
        if isinstance(index.data(OBJECT_ROLE),
                      (Enum, bool, int, float, str, bytes, type(None), dict, list, AbstractSet)):
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

    # todo redefine to match()
    def findItemByObj(self, obj) -> QModelIndex:
        for item in self.iterItems():
            print("Name:", item.data(NAME_ROLE))
            try:
                if item.data(OBJECT_ROLE) is obj:
                    return item
                if item.data(OBJECT_ROLE) == obj:
                    return item
            except AttributeError:
                continue
        return QModelIndex()

    def addItem(self, obj: Union[Package, SubmodelElement, Iterable],  # FIXME don't use update() instead use insertRow() and return index
                parent: QModelIndex = QModelIndex()):
        if isinstance(parent.data(OBJECT_ROLE), Submodel):
            # TODO change if they make Submodel iterable
            parentObj = self.objByIndex(parent).data(OBJECT_ROLE).submodel_element
        else:
            parentObj = self.objByIndex(parent).data(OBJECT_ROLE)

        if isinstance(parentObj, AbstractSet):
            parentObj.add(obj)
        elif isinstance(parentObj, list):
            parentObj.append(obj)
        elif isinstance(parentObj, dict):
            parentObj[obj.key] = obj.value
        elif parent.data(NAME_ROLE) in PACKAGE_ATTRS:
            parent.data(PACKAGE_ROLE).add(obj)
        elif isinstance(obj, Package):
            self.beginInsertRows(parent, self.rowCount(parent), self.rowCount(parent))
            item = PackTreeViewItem(obj, new=False)
            item.setParent(self.objByIndex(QModelIndex()))
            self.endInsertRows()
            return True
        else:
            raise AttributeError(
                f"Object couldn't be added: parent obj type is not appendable: {type(parentObj)}")
        self.update(parent)
        return True

    def update(self, index: QModelIndex):
        if not index.isValid():
            return QVariant()
        if self.hasChildren(index):
            self.removeRows(0, self.rowCount(index), index)
        self.beginInsertRows(index, self.rowCount(index), self.rowCount(index))
        self.objByIndex(index).populate()
        self.endInsertRows()
        self.dataChanged.emit(index, index.child(self.rowCount(index), self.columnCount(index)))
        return True

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if role == Qt.FontRole:
            return QFont(self.defaultFont)
        elif role == Qt.SizeHintRole:
            fontSize = self.defaultFont.pointSize()
            return QSize(-1, fontSize*1.7)
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignLeft | Qt.AlignBottom
        else:
            item = self.objByIndex(index)
            return item.data(role, index.column())

    def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        if not index.isValid() and not role == Qt.FontRole:
            return QVariant()
        elif role == Qt.FontRole:
            if isinstance(value, QFont):
                font = QFont(value)
                self.defaultFont.setPointSize(font.pointSize())
                self.dataChanged.emit(self.index(0), self.index(self.rowCount()))
        elif role == Qt.EditRole:
            try:
                if self.hasChildren(index):
                    self.removeRows(0, self.rowCount(index), index)
                value = None if str(value) == "None" else value
                item = self.objByIndex(index)
                if isinstance(index.parent().data(OBJECT_ROLE), list):
                    item.parentObj[index.row()] = value
                    item.obj = index.parent().data(OBJECT_ROLE)[index.row()]
                elif isinstance(index.parent().data(OBJECT_ROLE), AbstractSet):
                    item.parentObj.remove(item.obj)
                    item.parentObj.add(value)
                    item.obj = value
                elif isinstance(index.parent().data(OBJECT_ROLE), dict):
                    if index.column() == VALUE_COLUMN:
                        item.parentObj[item.objName] = value
                        item.obj = item.parentObj[item.objName]
                    elif index.column() == ATTRIBUTE_COLUMN:
                        item.parentObj[value] = item.parentObj.pop(item.objName)
                        item.objName = value
                else:
                    setattr(item.parentObj, item.objName, value)
                    item.obj = getattr(item.parentObj, item.objName)
                self.setChanged(index)
                item.populate()
                self.dataChanged.emit(index,
                                      index.child(self.rowCount(index), self.columnCount(index)))
                return True
            except (ValueError, AttributeError) as e:
                self.dataChanged.emit(index, index)
                # noinspection PyUnresolvedReferences
                self.valueChangeFailed.emit(
                    f"Error occurred while setting {self.objByIndex(index).objName}: {e}")
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
        parentObj = parentItem.obj

        # if parentObj is Submodel and the parentObj is not rootItem
        # set submodel_element as parentObj
        if isinstance(parentObj, Submodel) and parent.isValid():
            parentObj = parentItem.obj.submodel_element

        for n in range(row+count-1, row-1, -1):
            child = parentItem.children()[n]
            if isinstance(parentObj, list):
                parentItem.obj.pop[n]
                self.removeRows(row, count, parent)
                return True
            elif isinstance(parentObj, dict):
                parentObj.pop(child.objName)
                self.removeRows(row, count, parent)
                return True
            elif isinstance(parentObj, AbstractSet):
                parentObj.discard(child.obj)
                self.removeRows(row, count, parent)
                return True
            else:
                if not defaultVal == NOT_GIVEN:
                    self.setData(self.index(n, 0, parent), defaultVal, Qt.EditRole)
                    return True
                else:
                    self.valueChangeFailed.emit(
                        f"{child.objectName} could not be deleted or set to default")
                    return False

    def clearRow(self, row: int, parent: QModelIndex = ..., defaultVal=NOT_GIVEN) -> bool:
        """Delete row if it is child of Iterable else set to Default"""
        return self.clearRows(row, 1, parent, defaultVal)
