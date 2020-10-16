import collections

from PyQt5 import QtCore
from PyQt5.QtCore import Qt

from aas_editor.models import PACKAGE_ROLE, NAME_ROLE, OBJECT_ROLE, StandardItem
from aas_editor.settings import ATTRS_IN_PACKAGE_TREEVIEW
from aas_editor.util import getDescription


class PackTreeViewItem(StandardItem):
    def __init__(self, obj, parent=None, objName=None):
        super().__init__(obj, objName, parent)
        if parent:
            self.package = parent.data(PACKAGE_ROLE)
        else:
            self.package = obj
        self.populate()

    def populate(self):
        # todo make populate of PackTreeViewItem smarter (may be with typing check)
        try:
            for attr in ATTRS_IN_PACKAGE_TREEVIEW:
                if hasattr(self.obj, attr):
                    attr_obj = getattr(self.obj, attr)
                    parent = PackTreeViewItem(obj=attr_obj, parent=self, objName=attr)
                    if isinstance(attr_obj, collections.Iterable):
                        for i in attr_obj:
                            PackTreeViewItem(obj=i, parent=parent)
            for attr in ("submodel_element",):
                if hasattr(self.obj, attr):
                    attr_obj = getattr(self.obj, attr)
                    if attr_obj:
                        for i in attr_obj:
                            PackTreeViewItem(obj=i, parent=self)

        except (KeyError, NotImplementedError) as e:
            print(e)