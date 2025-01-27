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
import datetime
from enum import Enum
from typing import Dict, Type

from basyx.aas.model import NamespaceSet, LangStringSet
from basyx.aas.model.datatypes import Date
from dateutil.relativedelta import relativedelta

from aas_editor.additional.classes import DictItem
from aas_editor.import_feature import import_util
from aas_editor.utils import util, util_classes, util_type

IMPORT_FILE = "Motor Daten aus EMSRDB.xlsx"


class PreObjectImport(util_classes.PreObject):
    EXAMPLE_ROW_VALUE = None

    def __init__(self, objType, args, kwargs: Dict[str, object]):
        super(PreObjectImport, self).__init__(objType, args, kwargs)
        self._fromPreObjs2KwargObjs()
        paramsToAttrs: Dict[str, str] = util_classes.ClassesInfo.paramsToAttrs(objType)
        self.attrsToParams: Dict[str, str] = dict((v, k) for k, v in paramsToAttrs.items())

    @staticmethod
    def fromObject(obj, withIterParams=True):
        objType = type(obj)

        if isinstance(obj, PreObjectImport):
            return obj
        elif isinstance(obj, util_classes.PreObject):
            return PreObjectImport.fromPreObject(obj)

        if obj is None:
            return PreObjectImport.useExistingObject(obj)
        elif util_type.isoftype(objType, (bool, datetime.date, datetime.datetime, datetime.time)):
            return PreObjectImport(objType, (obj,), {})
        elif util_type.issubtype(objType, relativedelta):
            kwargs = {
                "years": PreObjectImport.fromObject(obj.years),
                "months": PreObjectImport.fromObject(obj.months),
                "days": PreObjectImport.fromObject(obj.days),
                "hours": PreObjectImport.fromObject(obj.hours),
                "minutes": PreObjectImport.fromObject(obj.minutes),
                "seconds": PreObjectImport.fromObject(obj.seconds),
                "microseconds": PreObjectImport.fromObject(obj.microseconds),
            }
            return PreObjectImport(objType, [], kwargs)
        elif util_type.issubtype(objType, (str, int, float, bytes)):
            return PreObjectImport(objType, (str(obj),), {})
        elif util_type.issubtype(objType, Enum):
            return PreObjectImport(objType, (obj,), {})
        elif util_type.issubtype(objType, Type) or objType == type:
            return PreObjectImport.useExistingObject(obj)
        elif util_type.issubtype(objType, dict):
            items = []
            for item in obj:
                key = PreObjectImport.fromObject(item)
                value = PreObjectImport.fromObject(obj[item])
                items.append((key, value))
            return PreObjectImport(objType, (items,), {})
        elif util_type.issubtype(objType, LangStringSet):
            items = PreObjectImport.fromObject(obj._dict)
            return PreObjectImport(objType, (items,), {})
        elif util_type.isSimpleIterableType(objType):
            objType = tuple if util_type.issubtype(objType, NamespaceSet) else objType
            items = []
            for item in obj:
                item = PreObjectImport.fromObject(item)
                items.append(item)
            return PreObjectImport(objType, (items,), {})
        else:
            kwargs = {}
            params = list(util.getReqParams4init(objType, rmDefParams=False, delOptional=False).keys())
            iterParams = util_classes.ClassesInfo.iterAttrs(objType)
            [params.remove(i) for i in iterParams]
            paramsToAttrs = util_classes.ClassesInfo.paramsToAttrs(objType)
            for param in params:
                attr = paramsToAttrs.get(param, param)
                val = getattr(obj, attr)
                val = PreObjectImport.fromObject(val)
                kwargs[param] = val
            if withIterParams:
                for iterParam in iterParams:
                    iterAttr = paramsToAttrs.get(iterParam, iterParam)
                    kwargs[iterParam] = getattr(obj, iterAttr)

            defaultParams2hide = dict(util_classes.ClassesInfo.defaultParamsToHide(objType))
            kwargs.update(defaultParams2hide)
            return PreObjectImport(objType, [], kwargs)

    @staticmethod
    def fromPreObject(preObj: util_classes.PreObject):
        if preObj.existingObjUsed:
            return PreObjectImport.useExistingObject(preObj.existingObj)
        else:
            return PreObjectImport(preObj.objType, preObj.args, preObj.kwargs)

    def _fromPreObjs2KwargObjs(self):
        args = []
        for arg in self.args:
            if isinstance(arg, util_classes.PreObject):
                arg = PreObjectImport.fromPreObject(arg)
            elif arg and type(arg) in (list, tuple) and isinstance(arg[0], util_classes.PreObject):
                arg = [PreObjectImport.fromPreObject(i) for i in arg]
            args.append(arg)

        kwargs = {}
        for key in self.kwargs:
            value = self.kwargs[key]
            if isinstance(value, util_classes.PreObject):
                value = PreObjectImport.fromPreObject(value)
            if isinstance(key, util_classes.PreObject):
                key = PreObjectImport.fromPreObject(key)
            kwargs[key] = value

        self.args = args
        self.kwargs = kwargs

    def initWithImport(self, rowNum, sourceWB, sheetname, fromSavedExampleRow=False):
        funcKwargs = {
            "rowNum": rowNum,
            "sourceWB": sourceWB,
            "sheetname": sheetname,
            "fromSavedExampleRow": fromSavedExampleRow
        }
        if self.existingObjUsed:
            return PreObjectImport._initObjWithImport(self.existingObj, objtype=self.objType, **funcKwargs)
        args = self._initWithImportArgs(**funcKwargs)
        kwargs = self._initWithImportKwargs(**funcKwargs)
        return self.objType(*args, **kwargs)

    @classmethod
    def _initObjWithImport(cls, obj, rowNum, sourceWB, sheetname, fromSavedExampleRow, objtype=None):
        if isinstance(obj, PreObjectImport):
            return obj.initWithImport(rowNum, sourceWB, sheetname, fromSavedExampleRow)
        elif isinstance(obj, str) and import_util.isValueToImport(obj):
            if fromSavedExampleRow:
                value = import_util.importValueFromExampleRow(obj, row=PreObjectImport.EXAMPLE_ROW_VALUE)
            else:
                value = import_util.importValueFromExcelWB(obj, workbook=sourceWB, row=rowNum, sheetname=sheetname)
            try:
                value = util_type.typecast(value, objtype)
            except Exception as e:
                print(f"Could not typecast value '{value}' to type '{objtype}': {e}")
            return value
        elif util_type.isSimpleIterable(obj):
            value = [PreObjectImport._initObjWithImport(i, rowNum, sourceWB, sheetname, fromSavedExampleRow) for i in
                     obj]
            return value
        elif objtype:
            try:
                value = util_type.typecast(obj, objtype)
                return value
            except Exception as e:
                print(f"Could not typecast value '{obj}' to type '{objtype}': {e}")
                return obj
        else:
            return obj

    def _initWithImportArgs(self, **funcKwargs):
        args = []
        if self.objType is dict and self.args:
            # args has following structure: ([(key1,val1), (key2,val2) ...])
            dictArgs = []
            dictItems = self.args[0]
            for dictItemPreObj in dictItems:
                dictItem = PreObjectImport._initObjWithImport(dictItemPreObj, **funcKwargs)
                if isinstance(dictItem, DictItem):
                    dictArgs.append((dictItem.key, dictItem.value))
                else:
                    # dictItem = (key1,val1)
                    dictArgs.append(dictItem)
            args.append(dictArgs)
        else:
            for val in self.args:
                initVal = PreObjectImport._initObjWithImport(val, **funcKwargs)
                args.append(initVal)
        return args

    def _initWithImportKwargs(self, **funcKwargs):
        kwargs = {}
        for key, val in self.kwargs.items():
            initVal = PreObjectImport._initObjWithImport(val, **funcKwargs)
            kwargs[key] = initVal
        return kwargs

    def initWithExampleRowImport(self):
        return self.initWithImport(rowNum=None, sourceWB=None, sheetname=None, fromSavedExampleRow=True)

    def __str__(self):
        if self.existingObjUsed:
            return str(self.existingObj)
        else:
            args = str(self.args).strip("[]")
            kwargs = ""
            for kwarg in self.kwargs:
                kwargs = f"{kwargs}, {kwarg}={self.kwargs[kwarg]}"
            if args and not kwargs:
                return f"{util_type.getTypeName(self.objType)}({args})"
            elif kwargs and not args:
                return f"{util_type.getTypeName(self.objType)}({kwargs})"
            else:
                return f"{util_type.getTypeName(self.objType)}({args}, {kwargs})"

    def __getattr__(self, item):
        param = self.attrsToParams.get(item, item)
        if param in self.kwargs:
            return self.kwargs[param]
        else:
            return object.__getattr__(util_classes.PreObject, item)

    def __iter__(self):
        if util_type.isIterableType(self.objType) and self.args:
            return iter(self.args[0])

    def items(self):
        if util_type.issubtype(self.objType, dict):
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
                        if obj.getMapping():
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
            for typ in TYPS_TO_SPECIAL_IMPORT_OBJ_CLASSES:
                if util_type.issubtype(self.objType, typ):
                    self.objType = TYPS_TO_SPECIAL_IMPORT_OBJ_CLASSES[typ]

            if isinstance(mapping, dict):
                for attr in mapping:
                    if isinstance(attr, int) or (isinstance(attr, str) and attr.isdecimal()):
                        preObj = self.args[0][int(attr)]
                    else:
                        preObj = self.kwargs[attr]
                    preObj.setMapping(mapping[attr])
            else:
                self.args = [mapping]


class DateImport(str):
    def __new__(cls, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], datetime.datetime):
            date: datetime.datetime = args[0].date()
            return Date(year=date.year, month=date.month, day=date.day)
        elif len(args) == 1 and isinstance(args[0], datetime.date):
            date = args[0]
            return Date(year=date.year, month=date.month, day=date.day)
        elif len(args) == 1 and isinstance(args[0], str):
            datetime_obj = datetime.datetime.fromisoformat(args[0])
            return Date(year=datetime_obj.year, month=datetime_obj.month, day=datetime_obj.day)
        else:
            raise TypeError("Value must be of type datetime.datetime or datetime.date or str in isoformat", args)


class TimeImport(str):
    def __new__(cls, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], datetime.time):
            return args[0]
        elif len(args) == 1 and isinstance(args[0], datetime.datetime):
            return args[0].time()
        elif len(args) == 1 and isinstance(args[0], str):
            datetime_obj = datetime.datetime.fromisoformat(args[0])
            return datetime_obj.time()
        else:
            raise TypeError("Value must be of type datetime.datetime or datetime.time or str in isoformat", args)


class DateTimeImport(str):
    def __new__(cls, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], datetime.datetime):
            return args[0]
        elif len(args) == 1 and isinstance(args[0], str):
            datetime_obj = datetime.datetime.fromisoformat(args[0])
            return datetime_obj
        else:
            raise TypeError("Value must be of type datetime.datetime or str in isoformat", args)


class BooleanImport(str):
    TRUE = ("1", "true", "yes", "ja", "wahr")
    FALSE = ("0", "false", "no", "nein", "falsch")

    def __new__(cls, *args, **kwargs):
        if len(args) == 1:
            value = args[0]
            if isinstance(value, (bool, int)):
                return bool(value)
            elif isinstance(value, str):
                value = value.lower()
                if value in BooleanImport.TRUE:
                    return True
                elif value in BooleanImport.FALSE:
                    return False
                else:
                    raise ValueError(f"Value must be one of the following values: "
                                     f"{BooleanImport.TRUE}, {BooleanImport.FALSE}")

        raise TypeError("Value must be of type Bool or Int or Str", args)


TYPS_TO_SPECIAL_IMPORT_OBJ_CLASSES = {
    datetime.time: TimeImport,
    datetime.datetime: DateTimeImport,
    datetime.date: DateImport,
    bool: BooleanImport,
}
