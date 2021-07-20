#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
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

from aas_editor.models import StandardItem
from aas_editor.settings.app_settings import PACKAGE_ROLE
from aas_editor.settings.aas_settings import TYPES_WITH_INSTANCES_NOT_TO_POPULATE, \
    TYPES_NOT_TO_POPULATE
from aas_editor.utils.util import getAttrs4detailInfo
from aas_editor.utils.util_type import getTypeName, isSimpleIterable
from aas_editor.utils.util_classes import DictItem
from aas_editor.package import Package


class DetailedInfoItem(StandardItem):
    def __init__(self, obj, name="", parent=None, package: Package = None, **kwargs):
        super().__init__(obj, name, parent, **kwargs)
        if parent and not package:
            self.package = parent.data(PACKAGE_ROLE)
        else:
            self.package = package
        self.populate()

    def populate(self):
        if isinstance(self.obj, TYPES_WITH_INSTANCES_NOT_TO_POPULATE) \
                or type(self.obj) in TYPES_NOT_TO_POPULATE:
            return

        kwargs = {
            "parent": self,
            "package": self.package,
            "new": self.new,
        }

        if isinstance(self.obj, dict):
            self._populateDict(self.obj, **kwargs)
        elif isSimpleIterable(self.obj):
            self._populateIterable(self.obj, **kwargs)
        else:
            self._populateUnknown(self.obj, **kwargs)

    @staticmethod
    def _populateDict(obj, **kwargs):
        for key, value in obj.items():
            DetailedInfoItem(DictItem(key, value), **kwargs)

    @staticmethod
    def _populateIterable(obj, **kwargs):
        for i, sub_item_obj in enumerate(obj):
            DetailedInfoItem(sub_item_obj,
                             name=f"{getTypeName(sub_item_obj.__class__)} {i}", **kwargs)

    @staticmethod
    def _populateUnknown(obj, **kwargs):
        for attr in getAttrs4detailInfo(obj):
            DetailedInfoItem(getattr(obj, attr), name=attr, **kwargs)
