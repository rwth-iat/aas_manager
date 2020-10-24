from PyQt5.QtCore import QObject, QVariant
from aas.model import AASReference

from aas_editor.settings import LINK_TYPES, PACKAGE_ROLE, NAME_ROLE, OBJECT_ROLE, ATTRIBUTE_COLUMN, \
    VALUE_COLUMN
from aas_editor.util import getDescription, getAttrDoc, simplifyInfo, getTypeName
from PyQt5.QtCore import Qt


class StandardItem(QObject):
    def __init__(self, obj, name=None, parent=None):
        super().__init__(parent)
        self.obj = obj
        self.objName = name

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
        if role == PACKAGE_ROLE:
            return self.package
        if role == Qt.DisplayRole:
            if column == ATTRIBUTE_COLUMN:
                return self.objectName
            if column == VALUE_COLUMN:
                return simplifyInfo(self.obj, self.objectName)
        if role == Qt.EditRole:
            if column == ATTRIBUTE_COLUMN:
                return self.objName
            if column == VALUE_COLUMN:
                return self.obj
        return QVariant()

    def setParent(self, a0: 'QObject') -> None:
        super().setParent(a0)
        try:
            self.package = a0.data(PACKAGE_ROLE)
        except AttributeError:
            pass

    @property
    def objectName(self):
        if self.objName:
            return self.objName
        elif hasattr(self.obj, "id_short") and self.obj.id_short:
            return self.obj.id_short
        else:
            return getTypeName(self.obj.__class__)

    @property
    def parentObj(self):
        try:
            return self.parent().obj
        except AttributeError:
            return None

    @property
    def isLink(self):
        if self.package and isinstance(self.obj, AASReference):
            try:
                self.obj.resolve(self.package.objStore)
                return True
            except (AttributeError, KeyError, NotImplementedError, TypeError) as e:
                print(e)
                return False
        # elif isinstance(self.obj, LINK_TYPES):
        #     return True
        return False

    def row(self):
        if self.parent():
            return self.parent().children().index(self)
        else:
            return 0
