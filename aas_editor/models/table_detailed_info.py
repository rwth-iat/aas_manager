import typing

from PyQt5.QtCore import pyqtSignal, QModelIndex, QVariant, Qt

from aas_editor.models import Package, COLUMNS_IN_DETAILED_INFO, DetailedInfoItem, StandardTable
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

    def replItemObj(self, obj, index: QModelIndex = QModelIndex()) -> QModelIndex:
        self.objByIndex(index).setData(obj, Qt.EditRole)
        self.objByIndex(index).populate()

        rows=self.rowCount()
        cols=self.columnCount()
        top_left=self.index(0,0)
        bot_right=self.index(rows-1, cols-1)
        self.dataChanged.emit(top_left, bot_right)
        return index