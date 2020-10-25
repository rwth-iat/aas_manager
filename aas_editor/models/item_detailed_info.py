from typing import AbstractSet

from aas_editor.models import StandardItem, Package
from aas_editor.settings import TYPES_NOT_TO_POPULATE
from aas_editor.util import getAttrs4detailInfo, getTypeName, isIterable


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

        if isinstance(self.obj, dict):
            self._populateDict(self.obj, **kwargs)
        elif isIterable(self.obj):
            self._populateIterable(self.obj, **kwargs)
        else:
            self._populateUnknown(self.obj, **kwargs)

    @staticmethod
    def _populateDict(obj, **kwargs):
        for attr, sub_item_obj in obj.items():
            kwargs["name"] = attr
            DetailedInfoItem(sub_item_obj, **kwargs)

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
