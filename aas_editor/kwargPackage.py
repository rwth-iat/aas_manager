#  Copyright (C) 2022  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
import copy
from pathlib import Path
from typing import Dict, Type, Union, List, Iterable

from basyx.aas.model import AssetAdministrationShell, Submodel, ConceptDescription

from aas_editor.package import Package, StoredFile
from aas_editor.utils.util import getParamsAndTypehints4init
from aas_editor.utils.util_classes import ClassesInfo, PreObject
from aas_editor.utils.util_type import getAttrTypeHint, isIterableType, isIterable, checkType, isOptional, getTypeName


class KwargPackage(Package):
    def __init__(self, file: Union[str, Path] = ""):
        """:raise TypeError if file has wrong file type"""
        super(KwargPackage, self).__init__(file)
        self._objStore: List[KwargObject] = [1]

    @property
    def shells(self) -> Iterable[AssetAdministrationShell]:
        return self._iter_objects(AssetAdministrationShell)

    @property
    def submodels(self) -> Iterable[Submodel]:
        return self._iter_objects(Submodel)

    @property
    def concept_descriptions(self) -> Iterable[ConceptDescription]:
        return self._iter_objects(ConceptDescription)


    def add(self, obj):
        if isinstance(obj, StoredFile):
            newName = self.fileStore.add_file(name=obj.name, file=obj.file(), content_type=obj.content_type)
            obj.setFileStore(newName, self.fileStore)
        else:
            self._objStore.append(obj)

    def discard(self, obj):
        self._objStore.remove(obj)

    def _iter_objects(self, objtype):
        for obj in self._objStore:
            if isinstance(obj, objtype):
                yield obj


class KwargObject:
    @staticmethod
    def getAttrTypeHint(obj, attr, delOptional=True):
        if isinstance(obj, KwargObject):
            return getAttrTypeHint(obj.objtype, attr, delOptional)
        else:
            raise TypeError("obj must be of Type: KwargObject!")

    def __init__(self, objtype, args, kwargs:Dict[str, object]):
        object.__setattr__(self, "args", args)
        object.__setattr__(self, "kwargs", kwargs)
        #self.args = args
        #self.kwargs = kwargs
        self.objtype = objtype
        self._updateKwargsWithDefaults()
        self._updateKwargsOptional()

        self.kwargs: Dict[str, object]
        self.kwargsTypehints: Dict[str, Type]
        self.kwargsOptional: Dict[str, bool]

        self.iterAttr = None

        self._checkIterability()
        self._fromPreObjs2KwargObjs()
        #self.__class__ = self.objtype

    def _checkIterability(self):
        if isIterableType(self.objtype):
            iterAttr = ClassesInfo.changedParentObject(self.objtype)
            iterAttrObj = self.kwargs[iterAttr]
            if not isIterable(iterAttrObj):
                if checkType(dict(), self.kwargsTypehints[iterAttr]):
                    self.kwargs[iterAttr] = dict()
                elif checkType(list(), self.kwargsTypehints[iterAttr]):
                    self.kwargs[iterAttr] = list()
                else:
                    raise TypeError("Unknown iterable type:", self.kwargsTypehints[iterAttr])
            self.setIterable(iterAttr)

    def _fromPreObjs2KwargObjs(self):
        args = []
        for arg in self.args:
            if isinstance(arg, PreObject):
                arg = KwargObject(arg.objType, arg.args, arg.kwargs)
            args.append(arg)

        kwargs = {}
        for key in self.kwargs:
            value = self.kwargs[key]
            if isinstance(value, PreObject):
                value = KwargObject(value.objType, value.args, value.kwargs)
            if isinstance(key, PreObject):
                key = KwargObject(key.objType, key.args, key.kwargs)
            kwargs[key] = value

        object.__setattr__(self, "args", args)
        object.__setattr__(self, "kwargs", kwargs)


    @property
    def __class__(self):
        return self.objtype

    def setIterable(self, iterAttr: str):
        #self.iterAttr = iterAttr
        self.__iter__ = lambda : iter(self.kwargs[iterAttr])

    # def __iter__(self):
    #     if self.iterAttr:
    #         return iter(self.kwargs[self.iterAttr])
    #     else:
    #         raise AttributeError

    def _updateKwargsWithDefaults(self):
        params, defaults = getParamsAndTypehints4init(self.objtype)
        self.kwargsTypehints = params
        if params and defaults:
            params = list(params.keys())
            revParams = list(reversed(params))
            defValues = list(defaults.values())
            revDefaults = list(reversed(defValues))
            for n, default in enumerate(revDefaults):
                param = revParams[n]
                if param not in self.kwargs:
                    if isinstance(default, tuple):
                        default = list(default)
                    self.kwargs[param] = default

    def _updateKwargsOptional(self):
        self.kwargsOptional = copy.copy(self.kwargsTypehints)
        for i in self.kwargsTypehints:
            typehint = self.kwargsTypehints[i]
            self.kwargsOptional[i] = True if isOptional(typehint) else False

    def initialize(self):
        return self.objtype(**self.kwargs)

    # def __getattribute__(self, name):
    #     if name in ("args", "kwargs"):
    #         return object.__getattribute__(self, name)
    #     elif name in self.kwargs:
    #         return self.kwargs[name]
    #     else:
    #         return object.__getattribute__(self, name)

    def __getattr__(self, item):
        if item in self.kwargs:
            return self.kwargs[item]
        else:
            raise AttributeError()
            #return object.__getattr__(self.objtype, item)

    def __setattr__(self, key, value):
        if key in ("args", "kwargs"):
            super(KwargObject, self).__setattr__(key, value)
        elif key in self.kwargs:
            self.kwargs[key] = value
        else:
            super(KwargObject, self).__setattr__(key, value)

    def __dir__(self) -> Iterable[str]:
        names = set([
    "_updateKwargsOptional",
    "_updateKwargsWithDefaults",
    "objtype",
    "args",
    "kwargs",
    "kwargsTypehints",
    "kwargsOptional",])
        names.update(self.kwargs.keys())
        return names

    def __str__(self):
        typename = getTypeName(self.objtype)
        args = str(self.args if self.args else '')
        kwargs = ""
        for key in self.kwargs:
            kwargs = f"{kwargs}{key}={self.kwargs[key]}, "
        kwargs.strip(" ").strip(",")
        if kwargs:
            kwargs = f"{kwargs})"
        return f"{typename}({args}{kwargs})"

    def __repr__(self):
        return self.__str__()

    # @property
    # def __class__(self):
    #     return self.objtype