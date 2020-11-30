from enum import Enum
from typing import Any, Iterable, Union, AbstractSet, List

from PyQt5.QtCore import QAbstractItemModel, QVariant, QModelIndex, Qt, pyqtSignal, QItemSelection, \
    QSize
from PyQt5.QtGui import QFont

from aas_editor.models import Package, DetailedInfoItem, StandardItem, PackTreeViewItem
from aas_editor.settings import NAME_ROLE, OBJECT_ROLE, ATTRIBUTE_COLUMN, VALUE_COLUMN, NOT_GIVEN, \
    PACKAGE_ROLE, PACK_ITEM_ROLE, PACKAGE_ATTRS, DEFAULT_FONT, ADD_ITEM_ROLE, CLEAR_ROW_ROLE, \
    DATA_CHANGE_FAILED_ROLE

from aas.model import Submodel, SubmodelElement

from aas_editor.util_classes import DictItem


class StandardTable(QAbstractItemModel):
    defaultFont = QFont(DEFAULT_FONT)

    def __init__(self, columns=("Item",), rootItem: StandardItem = None):
        super(StandardTable, self).__init__()
        self._rootItem = rootItem if rootItem else DetailedInfoItem(None, "") # FIXME
        self._columns = columns

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

        if (index.column() == ATTRIBUTE_COLUMN
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
        else:
            return super(StandardTable, self).match(start, role, value, hits, flags)

    def addItem(self, obj: Union[Package, SubmodelElement, Iterable],
                parent: QModelIndex = QModelIndex()):
        parent = parent.siblingAtColumn(0)
        parentObj = self.objByIndex(parent).data(OBJECT_ROLE)

        self.beginInsertRows(parent, self.rowCount(parent), self.rowCount(parent))
        if isinstance(obj, Package):
            item = PackTreeViewItem(obj, new=False, parent=self._rootItem)
        elif parent.data(NAME_ROLE) in PACKAGE_ATTRS:
            parent.data(PACKAGE_ROLE).add(obj)
            item = PackTreeViewItem(obj, parent=self.objByIndex(parent))
        elif isinstance(parent.data(OBJECT_ROLE), Submodel):
            # TODO change if they make Submodel iterable
            parentObj.submodel_element.add(obj)
            item = PackTreeViewItem(obj, parent=self.objByIndex(parent))
        elif isinstance(parentObj, AbstractSet):
            parentObj.add(obj)
            item = DetailedInfoItem(obj, "", parent=self.objByIndex(parent))
        elif isinstance(parentObj, list):
            parentObj.append(obj)
            item = DetailedInfoItem(obj, "", parent=self.objByIndex(parent))
        elif isinstance(parentObj, dict):
            parentObj[obj.key] = obj.value
            item = DetailedInfoItem(obj, obj.key, parent=self.objByIndex(parent))
        else:
            self.endInsertRows()
            raise AttributeError(
                f"Object couldn't be added: parent obj type is not appendable: {type(parentObj)}")
        self.endInsertRows()
        return self.index(item.row(), 0, parent)

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
        if not index.isValid() and role not in (Qt.FontRole, ADD_ITEM_ROLE):
            return QVariant()
        elif role == ADD_ITEM_ROLE:
            self.addItem(value, index)
            return True
        elif role == CLEAR_ROW_ROLE:
            self.clearRow(index.row(), index.parent(), value)
            return True
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
        elif role == Qt.EditRole:
            try:
                value = None if str(value) == "None" else value
                item = self.objByIndex(index)
                if isinstance(index.parent().data(OBJECT_ROLE), list):
                    item.parentObj[index.row()] = value
                    item.obj = index.parent().data(OBJECT_ROLE)[index.row()]
                elif isinstance(index.parent().data(OBJECT_ROLE), AbstractSet):
                    item.parentObj.remove(item.obj)
                    item.parentObj.add(value)
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
                # item.populate()
                # self.rowsInserted.emit(index, self.rowCount(index), self.columnCount(index))
                # self.dataChanged.emit(index,
                #                       index.child(self.rowCount(index), self.columnCount(index)))
                return True
            except (ValueError, AttributeError) as e:
                self.dataChanged.emit(index, index, [DATA_CHANGE_FAILED_ROLE])
                # noinspection PyUnresolvedReferences
                print(f"Error occurred while setting {self.objByIndex(index).objectName}: {e}")
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
        if isinstance(parentObj, Submodel) and parent.isValid():
            parentObj = parentObj.submodel_element

        for n in range(row+count-1, row-1, -1):
            child = parentItem.children()[n]
            if isinstance(parentObj, list):
                parentObj.pop[n]
                self.removeRows(row, count, parent)
                return True
            elif isinstance(parentObj, dict):
                parentObj.pop(child.objectName)
                self.removeRows(row, count, parent)
                return True
            elif isinstance(parentObj, AbstractSet):
                parentObj.discard(child.obj)
                self.removeRows(row, count, parent)
                return True
            elif parent.data(NAME_ROLE) in PACKAGE_ATTRS:
                parent.data(PACKAGE_ROLE).discard(child.obj)
                self.removeRows(row, count, parent)
                return True
            else:
                if not defaultVal == NOT_GIVEN:
                    self.setData(self.index(n, 0, parent), defaultVal, Qt.EditRole)
                    return True
                else:
                    self.dataChanged.emit(parent, parent, [DATA_CHANGE_FAILED_ROLE])
                    print(f"{child.objectName} could not be deleted or set to default")
                    return False

    def clearRow(self, row: int, parent: QModelIndex = ..., defaultVal=NOT_GIVEN) -> bool:
        """Delete row if it is child of Iterable else set to Default"""
        return self.clearRows(row, 1, parent, defaultVal)
