from types import GeneratorType

from PyQt5.QtGui import QBrush, QIcon, QColor
from PyQt5.QtCore import QObject, QVariant

from aas_editor.settings.app_settings import PACKAGE_ROLE, NAME_ROLE, OBJECT_ROLE, ATTRIBUTE_COLUMN, \
    VALUE_COLUMN, IS_LINK_ROLE, TYPE_HINT_ROLE, PARENT_OBJ_ROLE, TYPE_COLUMN, \
    TYPE_HINT_COLUMN, TYPE_CHECK_ROLE
from aas_editor.settings.aas_settings import TYPE_ICON_DICT, LINK_TYPES
from aas_editor.utils.util import getDescription, getAttrDoc, simplifyInfo
from aas_editor.utils.util_type import checkType, getTypeName, getTypeHintName, isIterable, \
    getAttrTypeHint, getIterItemTypeHint
from PyQt5.QtCore import Qt

from aas_editor.utils.util_classes import DictItem, ClassesInfo


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

    def __str__(self):
        return f"{getTypeName(type(self))}: {self.data(Qt.DisplayRole)}"

    @property
    def obj(self):
        try:
            obj = getattr(self.parentObj, self.objName)
            if not isinstance(obj, GeneratorType):
                return obj
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
        if role == TYPE_CHECK_ROLE:
            return checkType(self.obj, self.typehint)
        if role == PARENT_OBJ_ROLE:
            return self.parentObj
        if role == PACKAGE_ROLE:
            return self.package
        if role == IS_LINK_ROLE:
            return self.isLink
        if role == Qt.BackgroundRole:
            return self.bg
        if role == Qt.DecorationRole and column == 0:
            try:
                icon = TYPE_ICON_DICT[type(self.obj)]
                return QIcon(icon)
            except KeyError:
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
                try:
                    return getTypeHintName(self.typehint)
                except TypeError:
                    return str(self.typehint)
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
        if self.package and isinstance(self.obj, LINK_TYPES):
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

        if isIterable(self.parentObj):
            attrType = ClassesInfo.addType(type(self.parentObj))
            if not attrType and self.parent().data(TYPE_HINT_ROLE):
                parentTypehint = self.parent().data(TYPE_HINT_ROLE)
                try:
                    attrType = getIterItemTypeHint(parentTypehint)
                except KeyError:
                    print("Typehint could not be gotten")
        return attrType
