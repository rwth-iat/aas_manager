from PyQt5.QtCore import Qt, QVariant
from PyQt5.QtGui import QColor, QFont
from aas.model import AASReference, NamespaceSet

from aas_editor.models import TYPES_NOT_TO_POPULATE, VALUE_COLUMN, NAME_ROLE, OBJECT_ROLE, \
    PACKAGE_ROLE, ATTRIBUTE_COLUMN, STRING_ATTRS
from aas_editor.models.item_standard import StandardItem
from aas_editor.models.package import Package
from aas_editor.util import getAttrDoc, simplifyInfo, getAttrs4detailInfo


class DetailedInfoItem(StandardItem):
    def __init__(self, obj, name, parent=None, package: Package = None):
        super().__init__(obj, name, parent)
        self.package = package
        self.populate()

    def data(self, role, column=VALUE_COLUMN):
        if role == Qt.ToolTipRole:
            return getAttrDoc(self.objName, self.parentObj.__init__.__doc__)
        if role == NAME_ROLE:
            return self.objectName
        if role == OBJECT_ROLE:
            return self.obj
        if role == PACKAGE_ROLE:
            return self.package
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
                    # for child in self.children():
                    #     child.setParent(None)
                    #     # child.deleteLater()
                    self.populate()
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