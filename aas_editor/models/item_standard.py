from PyQt5.QtGui import QBrush, QIcon
from aas.model import AASReference, ConceptDescription, Event, RelationshipElement, Operation, \
    SubmodelElementCollection
from aas.model import *
from PyQt5.QtCore import QObject, QVariant

from aas_editor.settings import *
from aas_editor.settings import PACKAGE_ROLE, NAME_ROLE, OBJECT_ROLE, ATTRIBUTE_COLUMN, \
    VALUE_COLUMN, IS_LINK_ROLE
from aas_editor.util import getDescription, getAttrDoc, simplifyInfo, getTypeName, getAttrTypeHint, \
    isIterableType, issubtype, getTypeHintName
from PyQt5.QtCore import Qt


class StandardItem(QObject):
    def __init__(self, obj, name=None, parent=None, new=True, typehint=None):
        super().__init__(parent)
        self.obj = obj
        self.objName = name
        self.new = new
        self.changed = False
        self.bg = QBrush(QColor(0, 0, 0, 0))
        if typehint:
            self.typehint = typehint
        else:
            self.typehint = self.getTypeHint()

    @property
    def obj(self):
        try:
            return getattr(self.parentObj, self.objName)
        except (TypeError, AttributeError):
            pass
        return self._obj

    @obj.setter
    def obj(self, obj):
        self._obj = obj

    def setData(self, value, role, column=ATTRIBUTE_COLUMN):
        if role == Qt.BackgroundRole and isinstance(value, QBrush):
            self.bg = value
            return True
        return False

    def data(self, role, column=ATTRIBUTE_COLUMN):
        if role == Qt.WhatsThisRole:
            return getAttrDoc(self.objName, self.parentObj.__init__.__doc__)
        if role == Qt.ToolTipRole:
            try:
                return getDescription(self.obj.description)
            except AttributeError:
                pass
        if role == NAME_ROLE:
            return self.objectName
        if role == OBJECT_ROLE:
            return self.obj
        if role == TYPE_HINT_ROLE:
            return self.typehint
        if role == PARENT_OBJ_ROLE:
            return self.parentObj
        if role == PACKAGE_ROLE:
            return self.package
        if role == IS_LINK_ROLE:
            return self.isLink
        if role == Qt.BackgroundRole:
            return self.bg
        if role == Qt.DecorationRole and column == 0:
            for cls in TYPE_ICON_DICT:
                if isinstance(self.obj, cls):
                    icon = TYPE_ICON_DICT[cls]
                    return QIcon(icon)
            return QIcon()
        if role == Qt.DisplayRole:
            if column == ATTRIBUTE_COLUMN:
                return self.objectName
            if column == VALUE_COLUMN:
                return simplifyInfo(self.obj, self.objectName)
            if column == TYPE_COLUMN:
                return getTypeName(type(self.obj))
            if column == TYPE_HINT_COLUMN:
                return getTypeHintName(self.typehint)

        if role == Qt.EditRole:
            if column == ATTRIBUTE_COLUMN:
                return self.objectName
            if column == VALUE_COLUMN:
                if isinstance(self.obj, DictItem):
                    return self.obj.value
                return self.obj
        return QVariant()

    def setParent(self, a0: 'QObject') -> None:
        super().setParent(a0)
        if a0 is None:
            return
        if a0.data(PACKAGE_ROLE):
            try:
                self.package = a0.data(PACKAGE_ROLE)
            except AttributeError:
                return

    @property
    def objectName(self):
        if self.objName:
            return self.objName
        elif hasattr(self.obj, "id_short") and self.obj.id_short:
            return self.obj.id_short
        elif hasattr(self.obj, "name") and self.obj.name:
            return self.obj.name
        else:
            return getTypeName(self.obj.__class__)

    @property
    def parentObj(self):
        try:
            return self.parent().obj
        except AttributeError:
            return None

    @property
    def isLink(self) -> bool:
        if self.package and isinstance(self.obj, AASReference):
            try:
                self.obj.resolve(self.package.objStore)
                return True
            except (AttributeError, KeyError, NotImplementedError, TypeError) as e:
                print(e)
                return False
        return False

    def row(self):
        if self.parent():
            return self.parent().children().index(self)
        else:
            return 0

    def getTypeHint(self):
        attrType = None

        attr = self.data(NAME_ROLE)
        try:
            parentAttr = self.parent().data(NAME_ROLE)
        except AttributeError:
            return attrType

        try:
            attrType = getAttrTypeHint(type(self.parentObj), attr, delOptional=False)
            return attrType
        except KeyError:
            print("Typehint could not be gotten")

        if isIterableType(type(self.parentObj)):
            grandParentObj = self.parent().data(PARENT_OBJ_ROLE)
            try:
                parentAttrType = getAttrTypeHint(type(grandParentObj), parentAttr, delOptional=True)
                if issubtype(parentAttrType, dict):
                    DictItem._field_types["key"] = parentAttrType.__args__[0]
                    DictItem._field_types["value"] = parentAttrType.__args__[1]
                    attrType = DictItem
                else:
                    attrTypes = parentAttrType.__args__
                    if len(attrTypes) > 1:
                        raise KeyError("Typehint of iterable has more then one attribute:", attrTypes)
                    attrType = attrTypes[0]
            except KeyError:
                print("Typehint could not be gotten")
        return attrType
