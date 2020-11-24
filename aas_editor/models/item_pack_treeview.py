from aas_editor.models import StandardItem
from aas_editor.settings import ATTRS_IN_PACKAGE_TREEVIEW, PACKAGE_ROLE
from aas_editor.util import isIterable
from aas_editor.util_classes import Package


class PackTreeViewItem(StandardItem):
    def __init__(self, obj, parent=None, objName=None, new=True):
        super().__init__(obj, objName, parent, new=new)
        if isinstance(obj, Package):
            self.package = obj
        else:
            self.package = parent.data(PACKAGE_ROLE)
        self.populate()

    def populate(self):
        kwargs = {
            "parent": self,
            "new": self.new,
        }
        if isinstance(self.obj, Package):
            for attr in ATTRS_IN_PACKAGE_TREEVIEW:
                # set package objStore as obj, so that delete works
                PackTreeViewItem(self.obj.objStore, objName=attr, **kwargs)
        elif isIterable(self.obj):
            self._populateIterable(self.obj, **kwargs)

    @staticmethod
    def _populateIterable(obj, **kwargs):
        for sub_item_obj in obj:
            PackTreeViewItem(sub_item_obj, **kwargs)
