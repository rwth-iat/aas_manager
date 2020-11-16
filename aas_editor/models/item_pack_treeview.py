from aas_editor.models import StandardItem
from aas_editor.settings import ATTRS_IN_PACKAGE_TREEVIEW, PACKAGE_ROLE
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
        # todo make populate of PackTreeViewItem smarter (may be with typing check)
        try:
            for attr in ATTRS_IN_PACKAGE_TREEVIEW:
                # if obj is Package
                if hasattr(self.obj, attr):
                    # set package objStore as obj, so that delete works
                    PackTreeViewItem(obj=self.obj.objStore, parent=self,
                                     objName=attr, new=self.new)
                # if obj is shells or assets or submodels or concept_descriptions or others
                elif self.objName == attr:
                    items = getattr(self.parentObj, attr)
                    for i in items:
                        PackTreeViewItem(obj=i, parent=self, new=self.new)
            for attr in ("submodel_element",):
                if hasattr(self.obj, attr):
                    attr_obj = getattr(self.obj, attr)
                    if attr_obj:
                        for i in attr_obj:
                            PackTreeViewItem(obj=i, parent=self, new=self.new)
                            # todo ask if they want to make Submodel iterable, delete doesnt work

        except (KeyError, NotImplementedError) as e:
            print(e)
