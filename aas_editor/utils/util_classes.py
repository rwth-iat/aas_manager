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

from typing import NamedTuple, Any, Type, Tuple, Optional, List, Dict

from aas_editor.settings.util_constants import *
from aas_editor.settings import aas_settings as s


# DictItem = NamedTuple("DictItem", key=Any, value=Any)
from aas_editor.utils.util_type import issubtype


class DictItem(NamedTuple):
    key: Any
    value: Any

    @property
    def name(self):
        return self.key

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"{self.key}: {self.value}"


class ClassesInfo:
    @staticmethod
    def hasPackViewAttrs(cls) -> bool:
        if cls in s.CLASSES_INFO and PACKVIEW_ATTRS_INFO in s.CLASSES_INFO[cls]:
            return True
        return False

    @staticmethod
    def packViewAttrs(cls) -> List[str]:
        attrs = []
        if cls in s.CLASSES_INFO and PACKVIEW_ATTRS_INFO in s.CLASSES_INFO[cls]:
            attrs = list(s.CLASSES_INFO[cls][PACKVIEW_ATTRS_INFO].keys())
        return attrs

    @staticmethod
    def hiddenAttrs(cls) -> Tuple[str]:
        res = set()
        for typ in s.CLASSES_INFO:
            if issubclass(cls, typ):
                try:
                    res.update(s.CLASSES_INFO[typ][HIDDEN_ATTRS])
                except KeyError:
                    continue
        return tuple(res)

    @staticmethod
    def default_params_to_hide(cls) -> Dict[str, str]:
        res = dict()
        for typ in s.CLASSES_INFO:
            if issubtype(cls, typ):
                try:
                    res.update(s.CLASSES_INFO[typ][DEFAULT_PARAMS_TO_HIDE])
                except KeyError:
                    continue
        return res

    @staticmethod
    def params_to_attrs(cls) -> Dict[str, str]:
        res = dict()
        for typ in s.CLASSES_INFO:
            if issubtype(cls, typ):
                try:
                    res.update(s.CLASSES_INFO[typ][PARAMS_TO_ATTRS])
                except KeyError:
                    continue
        return res

    @staticmethod
    def addActText(cls, attr: Optional[str] = None) -> str:
        clsInfo = s.CLASSES_INFO.get(cls, {})

        if attr is None:
            res = clsInfo.get(ADD_ACT_AAS_TXT, "")
        else:
            attrsInfo = clsInfo.get(PACKVIEW_ATTRS_INFO, {})
            attrInfo = attrsInfo.get(attr, {})
            res = attrInfo.get(ADD_ACT_AAS_TXT, "")

        if not res:
            for typ in s.CLASSES_INFO:
                if issubclass(cls, typ):
                    try:
                        clsInfo = s.CLASSES_INFO[typ]
                        if attr is None:
                            return clsInfo[ADD_ACT_AAS_TXT]
                        else:
                            return clsInfo[PACKVIEW_ATTRS_INFO][attr][ADD_ACT_AAS_TXT]
                    except KeyError:
                        continue
        return res

    @staticmethod
    def changedParentObject(cls) -> str:
        clsInfo = s.CLASSES_INFO.get(cls, {})
        res = clsInfo.get(CHANGED_PARENT_OBJ, "")
        if not res:
            for typ in s.CLASSES_INFO:
                if issubclass(cls, typ):
                    try:
                        res = s.CLASSES_INFO[typ][CHANGED_PARENT_OBJ]
                        if cls is typ:
                            return res
                    except KeyError:
                        continue
        return res

    @staticmethod
    def addType(cls, attr: Optional[str] = None) -> Type:
        clsInfo = s.CLASSES_INFO.get(cls, {})
        if attr is None:
            res = clsInfo.get(ADD_TYPE, None)
        else:
            attrsInfo = clsInfo.get(PACKVIEW_ATTRS_INFO, {})
            attrInfo = attrsInfo.get(attr, {})
            res = attrInfo.get(ADD_TYPE, None)

        if not res:
            for typ in s.CLASSES_INFO:
                if issubclass(cls, typ):
                    try:
                        clsInfo = s.CLASSES_INFO[typ]
                        if attr is None:
                            return clsInfo[ADD_TYPE]
                        else:
                            return clsInfo[PACKVIEW_ATTRS_INFO][attr][ADD_TYPE]
                    except KeyError:
                        continue
        return res