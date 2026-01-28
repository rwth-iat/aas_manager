#  Copyright (C) 2022  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
import logging
from types import GeneratorType

from basyx.aas.adapter.aasx import DictSupplementaryFileContainer
from basyx.aas.model import ModelReference, Referable

from aas_editor.tools.import_feature.import_settings import MAPPING_ATTR
from aas_editor.models import PackTreeViewItem, StandardItem
from aas_editor.package import Package
from aas_editor.settings import PACKAGE_ROLE
from aas_editor.utils.util_classes import ClassesInfo
from aas_editor.utils.util_type import isIterable


class ImportTreeViewItem(PackTreeViewItem):
    def __init__(self, obj, parent, **kwargs):
        StandardItem.__init__(self, obj, parent=parent, **kwargs)
        if obj is None and parent is None:
            self.child = []
        elif isinstance(obj, Package):
            self.typehint = Package
            self.package = obj
        else:
            self.package = parent.data(PACKAGE_ROLE)

        if isinstance(obj, Referable):
            setattr(obj, MAPPING_ATTR, {})

        try:
            if isinstance(obj, ModelReference):
                obj = obj.resolve(self.package.objStore)
        except KeyError as e:
            logging.exception(e)
        self.obj = obj
        self.populate()

    def populate(self):
        kwargs = {
            "parent": self,
            "new": self.new,
        }
        if ClassesInfo.hasPackViewAttrs(type(self.obj)):
            for attr in ClassesInfo.packViewAttrs(type(self.obj)):
                # set package objStore as obj, so that delete works
                itemObj = getattr(self.obj, attr)
                packItem = ImportTreeViewItem(itemObj, name=attr, **kwargs)
                if isinstance(itemObj, GeneratorType):
                    packItem.obj = self.obj.objStore
        elif isIterable(self.obj):
            if isinstance(self.obj, DictSupplementaryFileContainer):
                self._populateFileContainer(self.obj, **kwargs)
            else:
                self._populateIterable(self.obj, **kwargs)

    @staticmethod
    def _populateIterable(obj, **kwargs):
        for sub_item_obj in obj:
            ImportTreeViewItem(sub_item_obj, **kwargs)

