from PyQt5.QtCore import Qt, QVariant
from PyQt5.QtGui import QColor, QFont
from aas.model import AASReference, NamespaceSet

from aas_editor.models import TYPES_NOT_TO_POPULATE, VALUE_COLUMN, NAME_ROLE, OBJECT_ROLE, \
    PACKAGE_ROLE, ATTRIBUTE_COLUMN, STRING_ATTRS
from aas_editor.models.item_standard import StandardItem
from aas_editor.models.package import Package
from aas_editor.util import getAttrDoc, simplifyInfo, getAttrs4detailInfo


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
                elif isinstance(self.parentObj, set):
                    self.parentObj.remove(self.obj)
                    self.parentObj.add(valueToSet)
                    self.obj = valueToSet
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