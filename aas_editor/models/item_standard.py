from PyQt5.QtCore import QObject, QVariant
from PyQt5.QtGui import QIcon
from aas.model import AASReference, ConceptDescription, Event, RelationshipElement, Operation, \
    SubmodelElementCollection
from aas.model import *
from PyQt5.QtCore import QObject, QVariant, QModelIndex
from aas.model import AASReference

from aas_editor.settings import *
from aas_editor.settings import LINK_TYPES, PACKAGE_ROLE, NAME_ROLE, OBJECT_ROLE, ATTRIBUTE_COLUMN, \
    VALUE_COLUMN, IS_LINK_ROLE
from aas_editor.util import getDescription, getAttrDoc, simplifyInfo, getTypeName
from PyQt5.QtCore import Qt
import qtawesome as qta

class StandardItem(QObject):
    def __init__(self, obj, name=None, parent=None, new=True):
        super().__init__(parent)
        self.obj = obj
        self.objName = name
        self.new = new
        self.changed = False

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
        if role == IS_LINK_ROLE:
            return self.isLink
        if role == Qt.DecorationRole and column == 0:
            if isinstance(self.obj, ConceptDescription):
                icon = qta.icon("mdi.text-box")
                icon = CONCEPT_ICON
            elif isinstance(self.obj, Event):
                icon = qta.icon("mdi.timeline-clock")  # mdi.timer mdi.bell
                icon = EVENT_ICON
            elif isinstance(self.obj, AnnotatedRelationshipElement):
                icon = qta.icon("mdi.arrow-left-right")  # mdi.relation-one-to-one
                icon = ANN_REL_ICON
            elif isinstance(self.obj, RelationshipElement):
                icon = qta.icon("mdi.arrow-left-right")  # mdi.relation-one-to-one
                icon = REL_ICON
            elif isinstance(self.obj, Operation):
                icon = qta.icon("mdi.cog")
                icon = OPERATION_ICON
            elif isinstance(self.obj, SubmodelElementCollectionUnordered):
                icon = COLLECT_ICON
            elif isinstance(self.obj, SubmodelElementCollectionOrdered):
                icon = qta.icon("mdi.package")
                icon = ORDER_COLLECT_ICON
            elif isinstance(self.obj, Entity):
                icon = ENTITY_ICON
            elif isinstance(self.obj, Capability):
                icon = CAPABILITY_ICON
            elif isinstance(self.obj, Asset):
                icon = qta.icon("mdi.mini-sd") # mdi.toy-brick
                icon = ASSET_ICON
            elif isinstance(self.obj, AssetAdministrationShell):
                icon = qta.icon("mdi.wallet") #  mdi.tab mdi.shredder folder-outline wallet
                icon = SHELL_ICON
            elif isinstance(self.obj, SubmodelElement):
                return
            elif isinstance(self.obj, Submodel):
                icon = SUBMODEL_ICON
            else:
                return
            return icon
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
