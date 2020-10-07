from PyQt5.QtCore import QAbstractItemModel, QVariant, QModelIndex, Qt

from aas_editor.models import OBJECT_ROLE, NAME_ROLE, Package, DetailedInfoItem


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
