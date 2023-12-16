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

from typing import Type, Tuple, Optional, List, Dict

from aas_editor.settings.util_constants import *
from aas_editor.settings import aas_settings as s


# DictItem = NamedTuple("DictItem", key=Any, value=Any)
from aas_editor.utils.util_type import issubtype, getTypeName


class PreObject:
    def __init__(self, objType, args, kwargs):
        self.kwargs: Dict[str, object] = kwargs
        self.args: List = list(args)
        self.objType: Type = objType

        self.existingObjUsed: bool = False if objType is not type(None) else True
        self.existingObj = None

    def __getattr__(self, item):
        if item in self.kwargs:
            return self.kwargs[item]
        else:
            return object.__getattr__(PreObject, item)

    def __str__(self):
        args = str(self.args).strip("[]")
        kwargs = ""
        for key, value in self.kwargs.items():
            kwargs = kwargs.join((f"{key}={value}",))
        try:
            typ = getTypeName(self.objType)
        except Exception as e:
            typ = str(self.objType)

        return f"PreObject({typ}, {args}, {kwargs})"

    def __repr__(self):
        return self.__str__()

    @classmethod
    def useExistingObject(cls, obj):
        """If object already exists and no PreObject needed"""
        c = cls(type(obj), [], {})
        c.existingObjUsed = True
        c.existingObj = obj
        return c

    def init(self):
        """Return initialized object"""
        if self.existingObjUsed:
            return self.existingObj

        args = self.initArgs()
        kwargs = self.initKwargs()

        try:
            return self.objType(*args, **kwargs)
        except TypeError:
            positional_arg_defaults = ClassesInfo.positional_arg_defaults(self.objType)
            for arg in positional_arg_defaults:
                kwargs[arg] = positional_arg_defaults[arg]
            for key in ClassesInfo.default_params_to_hide(object):
                try:
                    kwargs.pop(key)
                except KeyError:
                    continue
            return self.objType(*args, **kwargs)

    def initArgs(self):
        args = []
        for arg in self.args:
            if isinstance(arg, PreObject):
                arg = arg.init()
            elif arg and type(arg) == list and isinstance(arg[0], PreObject):
                arg = [i.init() for i in arg]
            args.append(arg)
        return args

    def initKwargs(self):
        kwargs = {}
        for key in self.kwargs:
            value = self.kwargs[key]
            if isinstance(value, PreObject):
                value = value.init()
            if isinstance(key, PreObject):
                key = key.init()
            kwargs[key] = value
        return kwargs

class ClassesInfo:
    @staticmethod
    def hasPackViewAttrs(cls) -> bool:
        for typ in s.CLASSES_INFO:
            if issubclass(cls, typ) and PACKVIEW_ATTRS_INFO in s.CLASSES_INFO[typ]:
                return True
        return False

    @staticmethod
    def packViewAttrs(cls) -> List[str]:
        attrs = set()
        for typ in s.CLASSES_INFO:
            if issubclass(cls, typ) and PACKVIEW_ATTRS_INFO in s.CLASSES_INFO[typ]:
                attrs.update(s.CLASSES_INFO[typ][PACKVIEW_ATTRS_INFO].keys())
        return list(attrs)

    @staticmethod
    def findInfoForClass(cls, attr: str, objToUpdate) -> List[object]:
        for typ in s.CLASSES_INFO:
            try:
                if issubtype(cls, typ):
                    try:
                        objToUpdate.update(s.CLASSES_INFO[typ][attr])
                    except KeyError:
                        continue
            except TypeError as e:
                print(f"{e}")
        return objToUpdate

    @staticmethod
    def hiddenAttrs(cls) -> Tuple[str]:
        return tuple(ClassesInfo.findInfoForClass(cls, HIDDEN_ATTRS, set()))

    @staticmethod
    def iterAttrs(cls) -> Tuple[str]:
        return tuple(ClassesInfo.findInfoForClass(cls, ITERABLE_ATTRS, set()))

    @staticmethod
    def default_params_to_hide(cls) -> Dict[str, str]:
        return ClassesInfo.findInfoForClass(cls, DEFAULT_PARAMS_TO_HIDE, dict())

    @staticmethod
    def positional_arg_defaults(cls) -> Dict[str, str]:
        return ClassesInfo.findInfoForClass(cls, POSITIONAL_ARG_DEFAULTS, dict())


    @staticmethod
    def params_to_attrs(cls) -> Dict[str, str]:
        return ClassesInfo.findInfoForClass(cls, PARAMS_TO_ATTRS, dict())

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
                if issubtype(cls, typ):
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
                if issubtype(cls, typ):
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
                if issubtype(cls, typ):
                    try:
                        clsInfo = s.CLASSES_INFO[typ]
                        if attr is None:
                            return clsInfo[ADD_TYPE]
                        else:
                            return clsInfo[PACKVIEW_ATTRS_INFO][attr][ADD_TYPE]
                    except KeyError:
                        continue
        return res