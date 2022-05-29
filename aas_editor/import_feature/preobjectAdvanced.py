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
import re
from enum import Enum
from typing import Dict, List, Type

import openpyxl

from aas_editor.utils.util import getReqParams4init
from aas_editor.utils.util_classes import PreObject, ClassesInfo
from aas_editor.utils.util_type import issubtype, isSimpleIterableType, getTypeName, isIterableType, isSimpleIterable

IMPORT_FILE = "Motor Daten aus EMSRDB.xlsx"
COLUMNS_PATTERN = re.compile(r"\$[A-Z][A-Z]?\$")


class PreObjectImport(PreObject):
    def __init__(self, objType, args, kwargs: Dict[str, object], obj=None):
        super(PreObjectImport, self).__init__(objType, args, kwargs)
        self.obj = obj
        self._fromPreObjs2KwargObjs()
        paramsToAttrs: Dict[str, str] = ClassesInfo.params_to_attrs(objType)
        self.attrsToParams: Dict[str, str] = dict((v, k) for k, v in paramsToAttrs.items())

    @staticmethod
    def fromObject(obj):
        objType = type(obj)

        if isinstance(obj, PreObjectImport):
            return obj
        elif isinstance(obj, PreObject):
            return PreObjectImport.fromPreObject(obj)

        if obj is None:
            return PreObjectImport(objType, [], {})
        elif issubtype(objType, bool):
            return PreObjectImport(objType, (obj,), {})
        elif issubtype(objType, (str, int, float, bytes)):
            return PreObjectImport(objType, (str(obj),), {})
        elif issubtype(objType, Enum):
            return PreObjectImport(objType, (obj,), {})
        elif issubtype(objType, Type):
            return PreObjectImport(objType, [], {}, obj=obj)
        elif issubtype(objType, dict):
            listObj = []
            for item in obj:
                key = PreObjectImport.fromObject(item)
                value = PreObjectImport.fromObject(obj[item])
                listObj.append((key, value))
            return PreObjectImport(objType, (listObj,), {})
        elif isSimpleIterableType(objType):
            listObj = []
            for item in obj:
                item = PreObjectImport.fromObject(item)
                listObj.append(item)
            return PreObjectImport(objType, (listObj,), {})
        else:
            kwargs = {}
            params = list(getReqParams4init(objType, rmDefParams=False, attrsToHide=ClassesInfo.default_params_to_hide(objType), delOptional=False).keys())
            iterParams = ClassesInfo.iterAttrs(objType)
            [params.remove(i) for i in iterParams]
            paramsToAttrs = ClassesInfo.params_to_attrs(objType)
            for param in params:
                attr = paramsToAttrs.get(param, param)
                val = getattr(obj, attr)
                val = PreObjectImport.fromObject(val)
                kwargs[param] = val
            for iterParam in iterParams:
                iterAttr = paramsToAttrs.get(iterParam, param)
                kwargs[param] = getattr(obj, iterAttr)
            return PreObjectImport(objType, [], kwargs)

    @staticmethod
    def fromPreObject(preObj: PreObject):
        return PreObjectImport(preObj.objType, preObj.args, preObj.kwargs, obj=getattr(preObj, "obj", None))

    def _fromPreObjs2KwargObjs(self):
        args = []
        for arg in self.args:
            if isinstance(arg, PreObject):
                arg = PreObjectImport(arg.objType, arg.args, arg.kwargs, obj=getattr(arg, "obj", None))
            elif arg and type(arg) == list and isinstance(arg[0], PreObject):
                arg = [PreObjectImport(i.objType, i.args, i.kwargs, obj=getattr(i, "obj", None)) for i in arg]
            args.append(arg)

        kwargs = {}
        for key in self.kwargs:
            value = self.kwargs[key]
            if isinstance(value, PreObject):
                value = PreObjectImport(value.objType, value.args, value.kwargs, obj=getattr(value, "obj", None))
            if isinstance(key, PreObject):
                key = PreObjectImport(key.objType, key.args, key.kwargs, obj=getattr(key, "obj", None))
            kwargs[key] = value

        self.args = args
        self.kwargs = kwargs

    def initWithImport(self):
        if self.obj:
            if isinstance(self.obj, str):
                if self.isValueToImport(self.obj):
                    self.obj = self.importValue(self.obj)
            return self.obj

        args = []
        for value in self.args:
            if isinstance(value, PreObjectImport):
                value = value.initWithImport()
            elif isinstance(value, str) and self.isValueToImport(value):
                value = self.importValue(value)
            elif value and type(value) == list and isinstance(value[0], PreObjectImport):
                value = [i.initWithImport() for i in value]
            args.append(value)

        kwargs = {}
        for key, value in self.kwargs.items():
            if isinstance(value, PreObjectImport):
                value = value.initWithImport()
            elif isinstance(value, str) and self.isValueToImport(value):
                value = self.importValue(value)
            kwargs[key] = value
        return self.objType(*args, **kwargs)

    def isValueToImport(self, value):
        if re.search(COLUMNS_PATTERN, value):
            return True
        return False

    def importValue(self, value):
        excel_file = openpyxl.load_workbook(IMPORT_FILE, data_only=True)
        sheet = excel_file.sheetnames[0]

        columns: List[str] = re.findall(COLUMNS_PATTERN, value)
        for col in columns:
            colName = col.strip("$")
            importedVal = excel_file[sheet][f"{colName}3"].value
            value = value.replace(f"${colName}$", importedVal, -1)
        return value

    def __str__(self):
        if self.obj:
            return str(self.obj)
        else:
            args = str(self.args).strip("[]")
            kwargs = ""
            for kwarg in self.kwargs:
                kwargs = f"{kwargs}, {kwarg}={self.kwargs[kwarg]}"
            if args and not kwargs:
                return f"{getTypeName(self.objType)}({args})"
            elif kwargs and not args:
                return f"{getTypeName(self.objType)}({kwargs})"
            else:
                return f"{getTypeName(self.objType)}({args}, {kwargs})"

    def __getattr__(self, item):
        param = self.attrsToParams.get(item, item)
        if param in self.kwargs:
            return self.kwargs[param]
        else:
            return object.__getattr__(PreObject, item)

    def __iter__(self):
        if isIterableType(self.objType) and self.args:
            return iter(self.args[0])

    def items(self):
        if issubtype(self.objType, dict):
            return self.args
        else:
            raise AttributeError(f"{self.objType} has no attribute 'items'")

    def getMapping(self) -> Dict[str, str]:
        mapping = {}
        if self.obj and isinstance(self.obj, str) and self.isValueToImport(self.obj):
            return str(self.obj)
        elif self.args:
            if len(self.args) > 1:
                raise NotImplementedError

            for i, value in enumerate(self.args):
                if isinstance(value, PreObjectImport):
                    return value.getMapping()
                elif isinstance(value, str) and self.isValueToImport(value):
                    return str(value)
                elif value and type(value) == list and isinstance(value[0], PreObjectImport):
                    for i, obj in enumerate(value):
                        mapping[i] = value.getMapping()
        elif self.kwargs:
            for key, value in self.kwargs.items():
                if isinstance(value, PreObjectImport):
                    map = value.getMapping()
                    if map:
                        mapping[key] = map
                elif isinstance(value, str) and self.isValueToImport(value):
                    mapping[key] = str(value)
        return mapping

    def setMapping(self, mapping: Dict[str, str]):
        if mapping:
            if isinstance(mapping, dict):
                for attr in mapping:
                    preObj = self.kwargs[attr]
                    preObj.setMapping(mapping[attr])
            else:
                self.args = [mapping]
