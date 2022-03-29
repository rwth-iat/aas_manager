#  Copyright (C) 2022  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
from typing import Union, Iterable

from PyQt5.QtCore import QModelIndex

from aas_editor.models import PacksTable, PackTreeViewItem
from aas_editor.package import Package
from aas_editor.kwargPackage import KwargObject
from aas_editor.settings import OBJECT_ROLE
from aas_editor.utils.util_classes import ClassesInfo


class ImportTable(PacksTable):
    def addItem(self, obj: Union[Package, 'SubmodelElement', Iterable],
                parent: QModelIndex = QModelIndex()):
        parent = parent.siblingAtColumn(0)
        parentItem = self.objByIndex(parent)
        parentObj = parentItem.data(OBJECT_ROLE)
        if isinstance(parentObj, KwargObject):
            parentObjCls = parentObj.objtype

            kwargs = {
                "obj": obj,
                "parent": parentItem,
            }

            if ClassesInfo.changedParentObject(parentObjCls):
                parentIterAttr = getattr(parentObj, ClassesInfo.changedParentObject(parentObjCls))
                if parentIterAttr is None:
                    parentIterAttr = list()
                parentIterAttr.append(obj)
                itemTyp = PackTreeViewItem
            else:
                raise AttributeError(
                    f"Object couldn't be added: parent obj type is not appendable: {type(parentObj)}")
            return self._addItem(parent, itemTyp, kwargs)
        else:
            return super(ImportTable, self).addItem(obj, parent)
