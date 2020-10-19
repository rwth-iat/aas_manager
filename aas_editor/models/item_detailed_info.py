from PyQt5.QtCore import Qt, QVariant
from aas.model import AASReference, NamespaceSet

from aas_editor.models import TYPES_NOT_TO_POPULATE, VALUE_COLUMN, NAME_ROLE, OBJECT_ROLE, \
    PACKAGE_ROLE, ATTRIBUTE_COLUMN
from aas_editor.models.item_standard import StandardItem
from aas_editor.models.package import Package
from aas_editor.util import getAttrDoc, simplifyInfo, getAttrs4detailInfo


class DetailedInfoItem(StandardItem):
    def __init__(self, obj, name, parent=None, package: Package = None):
        super().__init__(obj, name, parent)
        self.package = package
        self.populate()

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
