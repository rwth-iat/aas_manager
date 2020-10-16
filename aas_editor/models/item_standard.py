from PyQt5.QtCore import QObject, QVariant
from aas.model import AASReference

from aas_editor.models import PACKAGE_ROLE, NAME_ROLE, OBJECT_ROLE, VALUE_COLUMN, ATTRIBUTE_COLUMN
from aas_editor.settings import LINK_TYPES
from aas_editor.util import getDescription, getAttrDoc, simplifyInfo
from PyQt5.QtCore import Qt


class StandardItem(QObject):
    def __init__(self, obj, name=None, parent=None):
        super().__init__(parent)
        self.obj = obj
        self.objName = name

    def data(self, role, column=ATTRIBUTE_COLUMN):
        if role == Qt.ToolTipRole:
            if hasattr(self.obj, "description"):
                return getDescription(self.obj.description)
            else:
                return getAttrDoc(self.objName, self.parentObj.__init__.__doc__)
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
            return self.obj.__class__.__name__

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
            except (AttributeError, KeyError, NotImplementedError) as e:
                print(e)
        elif isinstance(self.obj, LINK_TYPES):
            return True
        return False

    def row(self):
        if self.parent():
            return self.parent().children().index(self)
        else:
            return 0