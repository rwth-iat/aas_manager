from typing import Any, Iterable

from PyQt5.QtCore import pyqtSignal, QModelIndex, QVariant, Qt
from PyQt5.QtGui import QColor, QFont

from aas_editor.models import Package, COLUMNS_IN_DETAILED_INFO, DetailedInfoItem, StandardTable, \
    VALUE_COLUMN, ATTRIBUTE_COLUMN, OBJECT_ROLE, NAME_ROLE, PACKAGE_ROLE


class DetailedInfoTable(StandardTable):
    valueChangeFailed = pyqtSignal(['QString'])

    def __init__(self, packItem: QModelIndex):
        self.mainObj = packItem.data(OBJECT_ROLE)
        self.package = packItem.data(PACKAGE_ROLE)
        root = DetailedInfoItem(self.mainObj, packItem.data(NAME_ROLE), package=self.package)
        super(DetailedInfoTable, self).__init__(COLUMNS_IN_DETAILED_INFO, root)

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        if role == Qt.BackgroundRole:
            return self._getBgColor(index)
        if role == Qt.ForegroundRole:
            return self._getFgColor(index)
        if role == Qt.FontRole:
            return self._getFont(index)
        item = self.objByIndex(index)
        return item.data(role, index.column())

    def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        if not index.isValid() or not role == Qt.EditRole:
            return QVariant()
        try:
            if self.hasChildren(index):
                self.removeRows(0, self.rowCount(index), index)
            value = None if str(value) == "None" else value
            item = self.objByIndex(index)
            if isinstance(index.parent().data(OBJECT_ROLE), list):
                item.parentObj[index.row()] = value
                item.obj = index.parent().data(OBJECT_ROLE)[index.row()]
            elif isinstance(index.parent().data(OBJECT_ROLE), set):
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
            if item.obj == value:
                item.populate()
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

    def insertRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        # todo implement
        pass

    def removeRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        parentObj = self.objByIndex(parent)

        self.beginRemoveRows(parent, row, row+count-1)
        for n in range(count):
            child = parentObj.children()[row]
            child.setParent(None)
            # child.deleteLater()
        self.endRemoveRows()
        return True

    def _getBgColor(self, index: QModelIndex):
        color = QColor(132, 185, 225)
        if index.parent().isValid():
            if index.row() == 0:
                color.setAlpha(260 - index.parent().data(Qt.BackgroundRole).alpha())
            else:
                color.setAlpha(
                    260 - index.siblingAtRow(index.row() - 1).data(Qt.BackgroundRole).alpha())
        else:
            if index.row() % 2:
                color.setAlpha(150)
            else:
                color.setAlpha(110)
        return color

    def _getFgColor(self, index: QModelIndex):
        if index.column() == VALUE_COLUMN:
            if self.objByIndex(index).isLink:
                return QColor(26, 13, 171)
        return QVariant()

    def _getFont(self, index: QModelIndex):
        font = QFont()
        if index.column() == ATTRIBUTE_COLUMN:
            if not isinstance(index.parent().data(OBJECT_ROLE), dict):
                font.setBold(True)
            return font
        if index.column() == VALUE_COLUMN:
            if self.objByIndex(index).isLink:
                font.setUnderline(True)
            return font
        return QVariant()

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags

        if (index.column() == ATTRIBUTE_COLUMN and not isinstance(index.parent().data(OBJECT_ROLE), dict)) \
                or self.hasChildren(index):
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
