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

import inspect
import typing
from abc import ABCMeta
from collections import abc
from enum import Enum
from typing import Union, Tuple, Iterable

from basyx.aas.model import AASReference

import aas_editor.additional.classes
from aas_editor import settings
import aas_editor.settings.aas_settings as aas_settings
from aas_editor.utils import util
from aas_editor.utils import util_classes

TYPING_TYPES = {typing.AbstractSet, typing.Callable, typing.Dict, typing.List, typing.NamedTuple,
                typing.NoReturn, typing.Set, typing.Sequence, typing.Tuple, typing.Type,
                typing.TypeVar, typing.Union}


def getOrigin(obj) -> typing.Type:
    """Return obj.__origin__ if it has it else return obj"""
    if hasattr(obj, "__origin__"):
        obj = obj.__origin__
    return obj


def getArgs(obj) -> typing.Tuple[typing.Type]:
    try:
        args = obj.__args__
    except AttributeError:
        args = tuple()
    return args


def isTypehint(obj) -> bool:
    obj = getOrigin(obj)
    try:
        if obj in TYPING_TYPES or type(obj) is typing.TypeVar:
            return True
    except TypeError as e:
        print(e)
    return inspect.isclass(obj)


def isUnion(typeHint):
    typ = getOrigin(typeHint)
    if typ == Union:
        return True
    return False


def isOptional(typeHint):
    if isUnion(typeHint):
        args = getArgs(typeHint)
        if type(None) in args:
            return True
    return False


def removeOptional(typehint):
    """Remove Nonetype from typehint if typehint is Optional[...], else return typehint"""
    if isOptional(typehint):
        args = list(getArgs(typehint))
        args.remove(type(None))
        typehint = args[0] if len(args) == 1 else typing.Union[tuple(args)]
    return typehint


def checkType(obj, typeHint):
    if typeHint is None:
        return True

    origin = getOrigin(typeHint)
    args = getArgs(typeHint)
    objType = type(obj)

    if objType == typeHint:
        return True

    if isUnion(typeHint):
        for typHint in args:
            if checkType(obj, typHint):
                return True
        else:
            return False

    if isinstance(obj, AASReference):
        return checkTypeAASRef(obj, typeHint)

    if isIterableType(origin) and objType is origin:
        return True

    if origin is abc.Iterable:
        return isIterableType(objType)

    return isinstance(obj, origin)


def checkTypeAASRef(aasref, typehint):
    """Check if"""
    if not isinstance(aasref, AASReference):
        raise TypeError("arg 1 must be of type AASReference")

    origin = getOrigin(typehint)
    args = getArgs(typehint)

    if origin is AASReference:
        if args:
            if isinstance(args[0], typing.ForwardRef):
                arg = args[0].__forward_arg__
                return getTypeName(aasref.type) == arg
            try:
                return issubclass(aasref.type, args)
            except TypeError as e:
                print(f"Error occured while checking: {aasref.type} and {args}", e)
                return False
        else:
            return True
    else:
        return False


def getTypeName(objType) -> str:
    if not isTypehint(objType) and not isoftype(objType, Enum):
        raise TypeError("Arg 1 must be type or typehint:", objType)

    nameAttrs = ("__name__", "_name", "name")
    for nameAttr in nameAttrs:
        try:
            if objType in aas_settings.TYPE_NAMES_DICT:
                res = aas_settings.TYPE_NAMES_DICT[objType]
                if isinstance(res, dict):
                    res = res["class"]
            else:
                res = getattr(objType, nameAttr)
            if res:
                break
        except (AttributeError, TypeError) as e:
            print(e)
            pass
    else:
        name = str(objType)
        # delete args if exist
        name = name.partition("[")[0]
        # delete type parents and return only type name
        res = name.rpartition(".")[2]
    return res


def getTypeHintName(typehint) -> str:
    if not isTypehint(typehint):
        raise TypeError("Arg 1 must be type or typehint:", typehint)

    optional = isOptional(typehint)
    if optional:
        typehint = removeOptional(typehint)
        optional = True

    typ = getTypeName(typehint)
    try:
        args = []
        for arg in typehint.__args__:
             args.append(getTypeHintName(arg))
        res = f"{typ}{args}".replace("'", "")
    except AttributeError:
        res = typ

    if optional:
        res = f"Optional[{res}]"

    return res


def issubtype(typ, types: Union[type, Tuple[Union[type, tuple], ...]]) -> bool:
    """
    Return whether 'typ' is a derived from another class or is the same class.
    The function also supports typehints. Checks whether typ is subtype of Typehint origin
    :param typ: type to check
    :param types: class or type annotation or tuple of classes or type annotations
    :raise TypeError if arg 1 or arg2 are not types or typehints:"
    """
    if not isTypehint(typ):
        raise TypeError("Arg 1 must be type or typehint:", typ)
    try:
        for tp in types:
            if not isTypehint(tp):
                raise TypeError("Arg 2 must be type, typehint or tuple of types/typehints:", types)
    except TypeError:
        if not isTypehint(types):
            raise TypeError("Arg 2 must be type, typehint or tuple of types/typehints:", types)

    try:
        if issubclass(types, Enum):
            return _issubtype(typ, types)
    except TypeError:
        pass

    if type(types) == typing.TypeVar:
        types = types.__bound__
        return issubtype(typ, types)

    try:
        for tp in types:
            if issubtype(typ, tp):
                return True
        return False
    except TypeError:
        return _issubtype(typ, types)


def _issubtype(typ1, typ2: type) -> bool:
    if isOptional(typ1):
        typA, typB = typ1.__args__
        typ1 = typA if typB is type(None) else typB

    if isUnion(typ1):
        if isUnion(typ2):
            return True
        else:
            return False
    if isUnion(typ2):
        if hasattr(typ2, "__args__") and typ2.__args__:
            typ2 = typ2.__args__
            return issubtype(typ1, typ2)
        else:
            return isUnion(typ1)

    if getTypeName(typ2) == "Type" and hasattr(typ2, "__args__") and typ2.__args__:
        args = typ2.__args__ if not isUnion(typ2.__args__[0]) else typ2.__args__[0].__args__
        if str(args[0]) == "+CT_co":  # type2 is just Type without args TODO fix later
            return getTypeName(typ1) == "Type"
        return issubtype(typ1, args)

    if hasattr(typ1, "__args__") and typ1.__args__:
        typ1 = typ1.__origin__
    if hasattr(typ2, "__args__") and typ2.__args__:
        typ2 = typ2.__origin__

    if type(None) in (typ1, typ2):
        return (typ1 == typ2)

    try:
        return issubclass(typ1, typ2)
    except TypeError:
        return issubclass(typ1.__origin__, typ2)


def isoftype(obj, types) -> bool:
    try:
        for tp in types:
            if not isTypehint(tp):
                raise TypeError("Arg 2 must be type, typehint or tuple of types/typehints:", types)
    except TypeError:
        if not isTypehint(types):
            raise TypeError("Arg 2 must be type, typehint or tuple of types/typehints:", types)

    try:
        if issubclass(types, Enum):
            return _isoftype(obj, types)
    except TypeError as e:
        print(e)

    try:
        for tp in types:
            if _isoftype(obj, tp):
                return True
        return False
    except TypeError as e:
        print(e)
        return _isoftype(obj, types)


def _isoftype(obj, typ) -> bool:
    if isUnion(typ) and hasattr(typ, "__args__") and typ.__args__:
        types = typ.__args__
        return isoftype(obj, types)

    if getTypeName(typ) == "Type" and hasattr(typ, "__args__") and typ.__args__:
        args = typ.__args__ if not isUnion(typ.__args__[0]) else typ.__args__[0].__args__
        if type(obj) in (type, ABCMeta):
            return issubtype(obj, args)
        else:
            return False

    #  TypeVar
    if hasattr(typ, "__bound__"):
        typ = typ.__bound__
        return issubtype(obj, typ)

    if hasattr(typ, "__args__") and typ.__args__:
        typ = typ.__origin__

    return isinstance(obj, typ)


def isSimpleIterableType(objType):
    if not isTypehint(objType):
        raise TypeError("Arg 1 must be type or typehint:", objType)

    if not issubtype(objType, settings.COMPLEX_ITERABLE_TYPES):
        return isIterableType(objType)
    else:
        return False


def isSimpleIterable(obj):
    return isSimpleIterableType(type(obj))


def isIterableType(objType):
    return issubtype(objType, Iterable) \
           and not issubtype(objType, (str, bytes, bytearray, aas_editor.additional.classes.DictItem))


def isIterable(obj):
    return isIterableType(type(obj))


def getAttrTypeHint(objType, attr, delOptional=True):
    params = util.getReqParams4init(objType, rmDefParams=False, delOptional=delOptional)
    if attr in params or f"{attr}_" in params:
        try:
            typeHint = params[attr]
        except KeyError:
            typeHint = params[f"{attr}_"]  # TODO fix if aas changes
    else:
        try:
            # get typehint of property
            func = getattr(objType, attr)
            typehints = typing.get_type_hints(func.fget)
            typeHint = typehints["return"]
        except Exception as e:
            print(e)
            raise KeyError

    try:
        if getArgs(typeHint):
            args = list(getArgs(typeHint))
            if ... in args:
                args.remove(...)
                typeHint.__args__ = args
            if Ellipsis in args:
                args.remove(Ellipsis)
                typeHint.__args__ = args
    except AttributeError:
        pass

    return typeHint


def getIterItemTypeHint(iterableTypehint):
    """Return typehint for item which shoulb be in iterable"""
    if not isTypehint(iterableTypehint):
        raise TypeError("Arg 1 must be type or typehint:", iterableTypehint)

    iterableTypehint = removeOptional(iterableTypehint)
    origin = getOrigin(iterableTypehint)
    args = getArgs(iterableTypehint)

    if issubtype(iterableTypehint, dict):
        aas_editor.additional.classes.DictItem._field_types["key"] = iterableTypehint.__args__[0]
        aas_editor.additional.classes.DictItem._field_types["value"] = iterableTypehint.__args__[1]
        attrType = aas_editor.additional.classes.DictItem
    elif args:
        if len(args) > 1:
            raise KeyError("Typehint of iterable has more then one attribute:", args)
        attrType = args[0]
    else:
        attrType = util_classes.ClassesInfo.addType(origin)

    if not isTypehint(attrType):
        raise TypeError("Found value is not type or typehint:", attrType)

    return attrType


def typeHintToType(typeHint):
    if issubtype(typeHint, typing.Dict):
        return dict
    elif issubtype(typeHint, typing.List):
        return list
    elif issubtype(typeHint, typing.Tuple):
        return tuple
    elif issubtype(typeHint, typing.Set):
        return set
    elif issubtype(typeHint, typing.Iterable):
        return list
    else:
        return typeHint


def typecast(val, typ):
    if type(val) is typ:
        return val

    if typ in (type, None):
        return val
    elif typ in (type(None),):
        return None
    else:
        return typ(val)