from typing import AbstractSet

from aas.model import AssetAdministrationShell, Submodel

from aas_editor.models import StandardItem
from aas_editor.settings import TYPES_NOT_TO_POPULATE, PACKAGE_ROLE
from aas_editor.util import getAttrs4detailInfo, getTypeName, isIterable
from aas_editor.util_classes import Package, DictItem


class DetailedInfoItem(StandardItem):
    def __init__(self, obj, name, parent=None, package: Package = None, new=True):
        super().__init__(obj, name, parent, new=new)
        if parent and not package:
            self.package = parent.data(PACKAGE_ROLE)
        else:
            self.package = package
        self.populate()

    def populate(self):
        if isinstance(self.obj, TYPES_NOT_TO_POPULATE):
            return

        kwargs = {
            "parent": self,
            "package": self.package,
            "new": self.new,
        }

        if isinstance(self.obj, dict):
            self._populateDict(self.obj, **kwargs)
        elif isIterable(self.obj) and not isinstance(self.obj, (Submodel, AssetAdministrationShell)):
            self._populateIterable(self.obj, **kwargs)
        else:
            self._populateUnknown(self.obj, **kwargs)

    @staticmethod
    def _populateDict(obj, **kwargs):
        for key, value in obj.items():
            kwargs["name"] = ""
            DetailedInfoItem(DictItem(key, value), **kwargs)

    @staticmethod
    def _populateIterable(obj, **kwargs):
        for i, sub_item_obj in enumerate(obj):
            kwargs["name"] = f"{getTypeName(sub_item_obj.__class__)} {i}"
            DetailedInfoItem(sub_item_obj, **kwargs)

    @staticmethod
    def _populateUnknown(obj, **kwargs):
        for attr in getAttrs4detailInfo(obj):
            kwargs["name"] = attr
            DetailedInfoItem(getattr(obj, attr), **kwargs)
