#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
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
from aas_editor.utils.util_type import getTypeName


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

    def __len__(self):
        obj = self.init()
        return len(obj)

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
        except TypeError as e:
            positional_arg_defaults = ClassesInfo.positionalArgDefaults(self.objType)
            for arg in positional_arg_defaults:
                kwargs[arg] = positional_arg_defaults[arg]
            # for key in ClassesInfo.defaultParamsToHide(object):
            for key in ClassesInfo.defaultParamsToHide(self.objType):
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
        hasAttrs = ClassesInfo.findSpecificInfoForClass(cls, PACKVIEW_ATTRS_INFO)
        if hasAttrs is not None:
            return True
        return False

    @staticmethod
    def isForbiddenToEditInGui(cls) -> bool:
        allowed = ClassesInfo.findSpecificInfoForClass(cls, IS_EDITABLE_IN_GUI)
        if allowed is not None:
            return not allowed
        return False

    @staticmethod
    def packViewAttrs(cls) -> List[str]:
        attrs = ClassesInfo.findSpecificInfoForClass(cls, PACKVIEW_ATTRS_INFO)
        return list(attrs) if attrs else list()

    @staticmethod
    def getClsAndItsParents(cls: Type) -> List[Type]:
        try:
            return cls.mro()
        except (TypeError, AttributeError):
            return [cls]

    @staticmethod
    def findAllInfoForClass(cls) -> Dict:
        cls_and_parents = ClassesInfo.getClsAndItsParents(cls)
        info = dict()
        # iterate over all classes and their parents to get all infos.
        # If a value is already in info, and it is iterable, update it such that the values are combined
        for cls in reversed(cls_and_parents):
            try:
                newinfo = s.CLASSES_INFO[cls]
                for key in newinfo:
                    if key in info:
                        if isinstance(info[key], (set, dict)):
                            info[key].update(newinfo[key])
                        elif isinstance(info[key], tuple):
                            info[key] = tuple(set(info[key] + newinfo[key]))
                    else:
                        info[key] = newinfo[key]
            except KeyError:
                pass
        return info

    @staticmethod
    def findSpecificInfoForClass(cls, infoType):
        cls_and_parents = ClassesInfo.getClsAndItsParents(cls)
        infos = []
        for cls in reversed(cls_and_parents):
            try:
                specificInfo = s.CLASSES_INFO[cls][infoType]
                infos.append(specificInfo)
            except KeyError:
                pass
        return ClassesInfo.unite(infos)

    @staticmethod
    def unite(infos):
        if not infos:
            return None

        if isinstance(infos[0], set):
            unitedinfo = set()
            for info in infos:
                unitedinfo.update(info)
        elif isinstance(infos[0], dict):
            unitedinfo = dict()
            for info in infos:
                unitedinfo.update(info)
        elif isinstance(infos[0], tuple):
            unitedinfo = tuple()
            for info in infos:
                unitedinfo = tuple(set(unitedinfo + info))
        else:
            unitedinfo = infos[-1]
        return unitedinfo

    @staticmethod
    def findInfoOnlyForClass(cls) -> Dict:
        info = dict()
        if cls in s.CLASSES_INFO:
            try:
                info.update(s.CLASSES_INFO[cls])
            except KeyError:
                pass
        return info

    @staticmethod
    def hiddenAttrs(cls) -> Tuple[str]:
        val = ClassesInfo.findSpecificInfoForClass(cls, HIDDEN_ATTRS)
        return val if val else tuple()

    @staticmethod
    def iterAttrs(cls) -> Tuple[str]:
        val = ClassesInfo.findSpecificInfoForClass(cls, ITERABLE_ATTRS)
        return val if val else tuple()

    @staticmethod
    def defaultParamsToHide(cls) -> Dict[str, str]:
        val = ClassesInfo.findSpecificInfoForClass(cls, DEFAULT_PARAMS_TO_HIDE)
        return val if val else dict()

    @staticmethod
    def positionalArgDefaults(cls) -> Dict[str, str]:
        val = ClassesInfo.findSpecificInfoForClass(cls, POSITIONAL_ARG_DEFAULTS)
        return val if val else dict()

    @staticmethod
    def paramsToAttrs(cls) -> Dict[str, str]:
        val = ClassesInfo.findSpecificInfoForClass(cls, PARAMS_TO_ATTRS)
        return val if val else dict()

    @staticmethod
    def addActText(cls, attr: Optional[str] = None) -> str:
        clsInfo = ClassesInfo.findAllInfoForClass(cls)

        if attr is None:
            res = clsInfo.get(ADD_ACT_AAS_TXT, "")
        else:
            attrsInfo = clsInfo.get(PACKVIEW_ATTRS_INFO, {})
            attrInfo = attrsInfo.get(attr, {})
            res = attrInfo.get(ADD_ACT_AAS_TXT, "")
        return res

    @staticmethod
    def changedParentObject(cls) -> str:
        clsInfo = ClassesInfo.findAllInfoForClass(cls)
        res = clsInfo.get(CHANGED_PARENT_OBJ, "")
        return res

    @staticmethod
    def addType(cls, attr: Optional[str] = None) -> Type:
        clsInfo = ClassesInfo.findAllInfoForClass(cls)
        if attr is None:
            res = clsInfo.get(ADD_TYPE, None)
        else:
            attrsInfo = clsInfo.get(PACKVIEW_ATTRS_INFO, {})
            attrInfo = attrsInfo.get(attr, {})
            res = attrInfo.get(ADD_TYPE, None)
        return res