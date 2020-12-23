from types import GeneratorType

from PyQt5.QtGui import QBrush, QIcon, QColor
from PyQt5.QtCore import QObject, QVariant

from aas_editor.package import StoredFile
from aas_editor.settings.app_settings import PACKAGE_ROLE, NAME_ROLE, OBJECT_ROLE, ATTRIBUTE_COLUMN, \
    VALUE_COLUMN, IS_LINK_ROLE, TYPE_HINT_ROLE, PARENT_OBJ_ROLE, TYPE_COLUMN, \
    TYPE_HINT_COLUMN, TYPE_CHECK_ROLE
from aas_editor.settings.aas_settings import TYPE_ICON_DICT, LINK_TYPES
from aas_editor.settings import FILE_ICON, FILETYPE_ICON_DICT
from aas_editor.utils.util import getDescription, getAttrDoc, simplifyInfo
from aas_editor.utils.util_type import checkType, getTypeName, getTypeHintName, isIterable, \
    getAttrTypeHint, getIterItemTypeHint
from PyQt5.QtCore import Qt

from aas_editor.utils.util_classes import DictItem, ClassesInfo


class StandardItem(QObject):
    def __init__(self, obj, name=None, parent=None, new=True, typehint=None):
        super().__init__(parent)
        self.new = new
        self.changed = False
        self.bg = QBrush(QColor(0, 0, 0, 0))

        # following attrs will be set during self.obj = obj
        self.displayValue = None
        self.typecheck = None
        self.objectName = None
        self.doc = None
        self.icon = QIcon()

        self._obj = obj
        self.objTypeName = getTypeName(type(self.obj))
        self.updateIcon()

        self.objName = name
        self.updateObjectName()
        self.doc = getAttrDoc(self.objName, self.parentObj.__init__.__doc__)
        self.displayValue = simplifyInfo(self.obj, self.objectName)

        self.typehint = typehint if typehint else self.getTypeHint()
        self.typecheck = checkType(self.obj, self.typehint)

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
        try:
            self.typecheck = checkType(self.obj, self.typehint)
        except AttributeError:
            pass
        self.objTypeName = getTypeName(type(self.obj))
        self.updateIcon()
        self.updateObjectName()
        self.doc = getAttrDoc(self.objName, self.parentObj.__init__.__doc__)
        self.displayValue = simplifyInfo(self.obj, self.objectName)

    @property
    def objName(self) -> str:
        return self._objName

    @objName.setter
    def objName(self, value):
        self._objName = value
        self.updateObjectName()
        self.doc = getAttrDoc(self.objName, self.parentObj.__init__.__doc__)
        self.displayValue = simplifyInfo(self.obj, self.objectName)

    @property
    def typehint(self) -> str:
        return self._typehint

    @typehint.setter
    def typehint(self, value):
        self._typehint = value
        self.typecheck = checkType(self.obj, self.typehint)
        self.updateTypehintName()

    def updateObjectName(self):
        if self.objName:
            self.objectName = self.objName
        elif hasattr(self.obj, "id_short") and self.obj.id_short:
            self.objectName = self.obj.id_short
        elif hasattr(self.obj, "name") and self.obj.name:
            self.objectName = self.obj.name
        else:
            self.objectName = getTypeName(self.obj.__class__)

    def updateTypehintName(self):
        try:
            self.typehintName = getTypeHintName(self.typehint)
        except TypeError as e:
            print(e)
            self.typehintName = str(self.typehint)

    def updateIcon(self):
        if isinstance(self.obj, StoredFile):
            try:
                self.obj: StoredFile
                contentType: str = self.obj.contentType
                self.icon = QIcon(FILETYPE_ICON_DICT[contentType])
            except KeyError:
                contentType = contentType.rsplit("/")[0]
                self.icon = QIcon(FILETYPE_ICON_DICT.get(contentType, FILE_ICON))
        else:
            try:
                self.icon = QIcon(TYPE_ICON_DICT[type(self.obj)])
            except KeyError:
                for cls in TYPE_ICON_DICT:
                    if isinstance(self.obj, cls):
                        self.icon = QIcon(TYPE_ICON_DICT[cls])

    def setData(self, value, role, column=ATTRIBUTE_COLUMN):
        if role == Qt.BackgroundRole and isinstance(value, QBrush):
            self.bg = value
            return True
        return False

    def data(self, role, column=ATTRIBUTE_COLUMN):
        if role == Qt.WhatsThisRole:
            return self.doc
        if role == NAME_ROLE:
            return self.objectName
        if role == OBJECT_ROLE:
            return self.obj
        if role == TYPE_HINT_ROLE:
            return self.typehint
        if role == TYPE_CHECK_ROLE:
            return self.typecheck
        if role == PARENT_OBJ_ROLE:
            return self.parentObj
        if role == PACKAGE_ROLE:
            return self.package
        if role == IS_LINK_ROLE:
            return self.isLink
        if role == Qt.BackgroundRole:
            return self.bg
        if role == Qt.DecorationRole and column == 0:
            return self.icon
        if role in (Qt.DisplayRole, Qt.ToolTipRole):
            if column == ATTRIBUTE_COLUMN:
                return self.objectName
            if column == VALUE_COLUMN:
                return self.displayValue
            if column == TYPE_COLUMN:
                return self.objTypeName
            if column == TYPE_HINT_COLUMN:
                return self.typehintName
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
        attrTypehint = None
        attrName = self.data(NAME_ROLE)

        try:
            attrTypehint = getAttrTypeHint(type(self.parentObj), attrName, delOptional=False)
            return attrTypehint
        except KeyError:
            print("Typehint could not be gotten")

        if isIterable(self.parentObj):
            attrTypehint = ClassesInfo.addType(type(self.parentObj))
            if not attrTypehint and self.parent().data(TYPE_HINT_ROLE):
                parentTypehint = self.parent().data(TYPE_HINT_ROLE)
                try:
                    attrTypehint = getIterItemTypeHint(parentTypehint)
                except KeyError:
                    print("Typehint could not be gotten")
        return attrTypehint
