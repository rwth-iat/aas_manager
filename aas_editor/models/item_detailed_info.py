from typing import AbstractSet

from aas.model import AASReference, NamespaceSet

from aas_editor.models import TYPES_NOT_TO_POPULATE
from aas_editor.models.item_standard import StandardItem
from aas_editor.models.package import Package
from aas_editor.util import getAttrs4detailInfo, getTypeName


class DetailedInfoItem(StandardItem):
    def __init__(self, obj, name, parent=None, package: Package = None):
        super().__init__(obj, name, parent)
        self.package = package
        self.populate()

    def populate(self):
        if isinstance(self.obj, TYPES_NOT_TO_POPULATE):
            return

        kwargs = {
            "parent": self,
            "package": self.package
        }

        if type(self.obj) is AASReference:
            obj = self.obj
            for attr in getAttrs4detailInfo(obj):
                kwargs["name"] = attr
                DetailedInfoItem(getattr(obj, attr), **kwargs)
        elif isinstance(self.obj, dict):
            for attr, sub_item_obj in self.obj.items():
                kwargs["name"] = attr
                DetailedInfoItem(sub_item_obj,**kwargs)
        elif isinstance(self.obj, (AbstractSet, list, tuple)):
            for i, sub_item_obj in enumerate(self.obj):
                kwargs["name"] = f"{getTypeName(sub_item_obj.__class__)} {i}"
                DetailedInfoItem(sub_item_obj, **kwargs)
        else:
            for attr in getAttrs4detailInfo(self.obj):
                kwargs["name"] = attr
                DetailedInfoItem(getattr(self.obj, attr), **kwargs)
