from typing import Any, Iterable

from PyQt5.QtCore import pyqtSignal, QModelIndex, QVariant, Qt

from aas_editor.models import Package, COLUMNS_IN_DETAILED_INFO, DetailedInfoItem, StandardTable, \
    VALUE_COLUMN
from aas_editor.util import getAttrs4detailInfo


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

    def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        if not index.isValid():
            return QVariant()
        try:
            if self.hasChildren(index):
                self.removeRows(0, self.rowCount(index), index)

            if self.objByIndex(index).setData(value, role, index.column()):
                self.dataChanged.emit(index,
                                      index.child(self.rowCount(index), self.columnCount(index)))
                return True
            else:
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

    def replItemObj(self, obj, index: QModelIndex = QModelIndex()) -> QModelIndex:
        index = index.siblingAtColumn(VALUE_COLUMN)
        # self.beginInsertRows(index, 0, self.rowCount(index))
        if self.setData(index, obj, Qt.EditRole):
            # self.objByIndex(index).populate()
            # rows=self.rowCount(index)
            # cols=self.columnCount(index)
            # top_left=self.index(0,0)
            # bot_right=self.index(rows-1, cols-1)
            # self.dataChanged.emit(index, index.child(self.rowCount(index), self.columnCount(index)))
            # self.endInsertRows()
            return index
        return QModelIndex()

    def insertRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        # todo implement
        pass

    def removeRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        parentObj = self.objByIndex(parent)
        if not isinstance(parentObj.obj, Iterable):
            return False

        self.beginRemoveRows(parent, row, row+count-1)
        for n in range(count):
            child = parentObj.children()[row]
            child.setParent(None)
            # child.deleteLater()
        self.endRemoveRows()
        return True

    def revert(self) -> None:
        pass
        # todo implement for row editing