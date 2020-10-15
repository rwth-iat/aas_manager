from typing import Any

from PyQt5.QtCore import QAbstractItemModel, QVariant, QModelIndex, Qt

from aas_editor.models import OBJECT_ROLE, NAME_ROLE, Package, DetailedInfoItem, StandardItem


class StandardTable(QAbstractItemModel):
    def __init__(self, columns=("Item",), rootItem: StandardItem = None):
        super(StandardTable, self).__init__()
        self._rootItem = rootItem if rootItem else DetailedInfoItem(None, "", None)
        self._columns = columns

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        return self.objByIndex(index).data(role)

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

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.objByIndex(parent).children())

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self._columns)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> Any:
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._columns[section]

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def hasChildren(self, parent: QModelIndex = ...) -> bool:
        return True if self.rowCount(parent) else False

    def objByIndex(self, index: QModelIndex):
        if not index.isValid():
            return self._rootItem
        return index.internalPointer()

    def iterItems(self, parent: QModelIndex = QModelIndex()):
        def recurse(parent):
            for row in range(self.rowCount(parent)):
                childIndex = self.index(row, 0, parent)
                yield childIndex
                child = self.objByIndex(childIndex)
                if child.children():
                    yield from recurse(childIndex)

        yield from recurse(parent)

    def findItemByObj(self, obj): #todo redefine to match()
        for item in self.iterItems():
            print("Name:", item.data(NAME_ROLE))
            try:
                if item.data(OBJECT_ROLE) == obj:
                    return item
            except AttributeError:
                continue

    def addItem(self, item, parent: QModelIndex = QModelIndex()): # todo redefine to insertRows
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

