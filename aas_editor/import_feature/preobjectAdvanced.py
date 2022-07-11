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

from aas_editor.import_feature import import_util
from aas_editor.utils.util import getReqParams4init
from aas_editor.import_feature import import_file_widget
from aas_editor.utils.util_classes import PreObject, ClassesInfo
from aas_editor.utils.util_type import issubtype, isSimpleIterableType, getTypeName, isIterableType, isSimpleIterable

IMPORT_FILE = "Motor Daten aus EMSRDB.xlsx"


class PreObjectImport(PreObject):
    def __init__(self, objType, args, kwargs: Dict[str, object]):
        super(PreObjectImport, self).__init__(objType, args, kwargs)
        self._fromPreObjs2KwargObjs()
        paramsToAttrs: Dict[str, str] = ClassesInfo.params_to_attrs(objType)
        self.attrsToParams: Dict[str, str] = dict((v, k) for k, v in paramsToAttrs.items())

    @staticmethod
    def fromObject(obj, withIterParams=True):
        objType = type(obj)

        if isinstance(obj, PreObjectImport):
            return obj
        elif isinstance(obj, PreObject):
            return PreObjectImport.fromPreObject(obj)

        if obj is None:
            return PreObjectImport.useExistingObject(obj)
        elif issubtype(objType, bool):
            return PreObjectImport(objType, (obj,), {})
        elif issubtype(objType, (str, int, float, bytes)):
            return PreObjectImport(objType, (str(obj),), {})
        elif issubtype(objType, Enum):
            return PreObjectImport(objType, (obj,), {})
        elif issubtype(objType, Type) or objType == type:
            return PreObjectImport.useExistingObject(obj)
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
            params = list(getReqParams4init(objType, rmDefParams=False, delOptional=False).keys())
            iterParams = ClassesInfo.iterAttrs(objType)
            [params.remove(i) for i in iterParams]
            paramsToAttrs = ClassesInfo.params_to_attrs(objType)
            for param in params:
                attr = paramsToAttrs.get(param, param)
                val = getattr(obj, attr)
                val = PreObjectImport.fromObject(val)
                kwargs[param] = val
            if withIterParams:
                for iterParam in iterParams:
                    iterAttr = paramsToAttrs.get(iterParam, iterParam)
                    kwargs[iterParam] = getattr(obj, iterAttr)

            defaultParams2hide = dict(ClassesInfo.default_params_to_hide(objType))
            kwargs.update(defaultParams2hide)
            return PreObjectImport(objType, [], kwargs)

    @staticmethod
    def fromPreObject(preObj: PreObject):
        if preObj.existingObjUsed:
            return PreObjectImport.useExistingObject(preObj.existingObj)
        else:
            return PreObjectImport(preObj.objType, preObj.args, preObj.kwargs)

    def _fromPreObjs2KwargObjs(self):
        args = []
        for arg in self.args:
            if isinstance(arg, PreObject):
                arg = PreObjectImport.fromPreObject(arg)
            elif arg and type(arg) == list and isinstance(arg[0], PreObject):
                arg = [PreObjectImport.fromPreObject(i) for i in arg]
            args.append(arg)

        kwargs = {}
        for key in self.kwargs:
            value = self.kwargs[key]
            if isinstance(value, PreObject):
                value = PreObjectImport.fromPreObject(value)
            if isinstance(key, PreObject):
                key = PreObjectImport.fromPreObject(key)
            kwargs[key] = value

        self.args = args
        self.kwargs = kwargs

    def initWithImport(self, rowNum, sourceWB, sheetname):
        if self.existingObjUsed:
            if isinstance(self.existingObj, str):
                if import_util.isValueToImport(self.existingObj):
                    self.existingObj = import_util.importValueFromExcelWB(self.existingObj, workbook=sourceWB, row=rowNum, sheetname=sheetname)
            return self.existingObj

        args = []
        for value in self.args:
            if isinstance(value, PreObjectImport):
                value = value.initWithImport(rowNum, sourceWB, sheetname)
            elif isinstance(value, str) and import_util.isValueToImport(value):
                value = import_util.importValueFromExcelWB(value, workbook=sourceWB, row=rowNum, sheetname=sheetname)
            elif value and type(value) == list and isinstance(value[0], PreObjectImport):
                value = [i.initWithImport(rowNum, sourceWB, sheetname) for i in value]
            args.append(value)

        kwargs = {}
        for key, value in self.kwargs.items():
            if isinstance(value, PreObjectImport):
                value = value.initWithImport(rowNum, sourceWB, sheetname)
            elif isinstance(value, str) and import_util.isValueToImport(value):
                value = import_util.importValueFromExcelWB(value, workbook=sourceWB, row=rowNum, sheetname=sheetname)
            kwargs[key] = value
        try:
            return self.objType(*args, **kwargs)
        except Exception as e:
            raise e

    def initWithExampleRowImport(self):
        exampleRow = import_file_widget.ImportManageWidget.IMPORT_SETTINGS.exampleRowValue

        if self.existingObjUsed:
            if isinstance(self.existingObj, str):
                if import_util.isValueToImport(self.existingObj):
                    self.existingObj = import_util.importValueFromExampleRow(self.existingObj, row=exampleRow)
            return self.existingObj

        args = []
        for value in self.args:
            if isinstance(value, PreObjectImport):
                value = value.initWithExampleRowImport()
            elif isinstance(value, str) and import_util.isValueToImport(value):
                value = import_util.importValueFromExampleRow(value, row=exampleRow)
            elif value and type(value) == list and isinstance(value[0], PreObjectImport):
                value = [i.initWithExampleRowImport() for i in value]
            args.append(value)

        kwargs = {}
        for key, value in self.kwargs.items():
            if isinstance(value, PreObjectImport):
                value = value.initWithExampleRowImport()
            elif isinstance(value, str) and import_util.isValueToImport(value):
                value = import_util.importValueFromExampleRow(value, row=exampleRow)
            kwargs[key] = value
        return self.objType(*args, **kwargs)

    def __str__(self):
        if self.existingObjUsed:
            return str(self.existingObj)
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
        if self.existingObjUsed and isinstance(self.existingObj, str) and import_util.isValueToImport(self.existingObj):
            return str(self.existingObj)
        elif self.args:
            if len(self.args) > 1:
                raise NotImplementedError

            for i, value in enumerate(self.args):
                if isinstance(value, PreObjectImport):
                    return value.getMapping()
                elif isinstance(value, str) and import_util.isValueToImport(value):
                    return str(value)
                elif value and type(value) == list and isinstance(value[0], PreObjectImport):
                    for i, obj in enumerate(value):
                        mapping[i] = obj.getMapping()
        elif self.kwargs:
            for key, value in self.kwargs.items():
                if isinstance(value, PreObjectImport):
                    map = value.getMapping()
                    if map:
                        mapping[key] = map
                elif isinstance(value, str) and import_util.isValueToImport(value):
                    mapping[key] = str(value)
        return mapping

    def setMapping(self, mapping: Dict[str, str]):
        if mapping:
            if isinstance(mapping, dict):
                for attr in mapping:
                    if isinstance(attr, int) or (isinstance(attr, str) and attr.isdecimal()):
                        preObj = self.args[0][int(attr)]
                    else:
                        preObj = self.kwargs[attr]
                    preObj.setMapping(mapping[attr])
            else:
                self.args = [mapping]
