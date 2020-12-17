import inspect
import typing
from abc import ABCMeta
from collections import abc
from enum import Enum
from typing import Union, Tuple, Iterable

from aas.model import AASReference

from aas_editor.settings.aas_settings import COMPLEX_ITERABLE_TYPES
from aas_editor.util import getReqParams4init
from aas_editor.util_classes import DictItem


def checkType(obj, typeHint):
    if typeHint is None:
        return True

    if isUnion(typeHint):
        for typHint in typeHint.__args__:
            if checkType(obj, typHint):
                return True
        else:
            return False

    typ = type(obj)

    try:
        origin = typeHint.__origin__
    except AttributeError:
        origin = typeHint

    try:
        args = typeHint.__args__
    except AttributeError:
        args = tuple()

    if typ == typeHint:
        return True

    if isinstance(obj, AASReference):
        if origin == AASReference:
            if args:
                if isinstance(args[0], ForwardRef):
                    arg = args[0].__forward_arg__
                    return getTypeName(obj.type) == arg
                try:
                    return issubclass(obj.type, args)
                except TypeError as e:
                    print(f"Error occured while checking: {obj.type} and {args}", e)
                    return False
            else:
                return True
        else:
            return False

    if isIterableType(origin) and typ is origin:
        return True

    if origin is abc.Iterable:
        return isIterableType(typ)

    return isinstance(obj, origin)


def getTypeName(objType) -> str:
    try:
        res = objType.__name__
    except AttributeError:
        try:
            res = objType._name
        except AttributeError:
            try:
                res = objType.name
            except AttributeError:
                name = str(objType)
                # delete args if exist
                name = name.partition("[")[0]
                # delete type parents and return only type name
                res = name.rpartition(".")[2]
    return res


def getTypeHintName(typehint) -> str:
    typ = getTypeName(typehint)
    try:
        args = []
        for arg in typehint.__args__:
             args.append(getTypeHintName(arg))
        return f"{typ}{args}".replace("'", "")
    except AttributeError:
        return typ


def removeOptional(typehint):
    """Remove Nonetype from typehint if typehint is Optional[...]"""
    if isOptional(typehint):
        args = list(typehint.__args__)
        args.remove(type(None))
        typehint = args[0]
    return typehint


def isOptional(typeHint):
    if isUnion(typeHint):
        if type(None) in typeHint.__args__:
            if len(typeHint.__args__) == 2:
                return True
    return False


def isUnion(typeHint):
    if hasattr(typeHint, "__origin__"):
        typeHint = typeHint.__origin__
    if typeHint == Union:
        return True
    return False


def issubtype(typ, types: Union[type, Tuple[Union[type, tuple], ...]]) -> bool:
    """
    Return whether 'typ' is a derived from another class or is the same class.
    The function also supports typehints. Checks whether typ is subtype of Typehint origin
    :param typ: type to check
    :param types: class or type annotation or tuple of classes or type annotations
    :raise TypeError if arg 1 or arg2 are not types or typehints:"
    """
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

    if not inspect.isclass(typ1):
        raise TypeError("Arg 1 must be type or typehint:", typ1)
    if not inspect.isclass(typ2):
        raise TypeError("Arg 2 must be type or typehint:", typ2)

    try:
        return issubclass(typ1, typ2)
    except TypeError:
        return issubclass(typ1.__origin__, typ2)


def isoftype(obj, types) -> bool:
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
    if not issubtype(objType, COMPLEX_ITERABLE_TYPES):
        return isIterableType(objType)
    else:
        return False


def isSimpleIterable(obj):
    return isSimpleIterableType(type(obj))


def isIterableType(objType):
    return issubtype(objType, Iterable) and not issubtype(objType, (str, bytes, bytearray, DictItem))


def isIterable(obj):
    return isIterableType(type(obj))


def getAttrTypeHint(objType, attr, delOptional=True):
    params = getReqParams4init(objType, rmDefParams=False, delOptional=delOptional)
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
        if typeHint.__args__:
            args = list(typeHint.__args__)
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
    iterableTypehint = removeOptional(iterableTypehint)

    if issubtype(iterableTypehint, dict):
        DictItem._field_types["key"] = iterableTypehint.__args__[0]
        DictItem._field_types["value"] = iterableTypehint.__args__[1]
        attrType = DictItem
    else:
        attrTypes = iterableTypehint.__args__
        if len(attrTypes) > 1:
            raise KeyError("Typehint of iterable has more then one attribute:", attrTypes)
        attrType = attrTypes[0]
    return attrType


TYPING_TYPES = set(
    typing.AbstractSet,
    typing.Callable,
    typing.Dict,
    typing.List,
    typing.Literal,
    typing.NamedTuple,
    typing.NoReturn,
    typing.Protocol,
    typing.Set,
    typing.Sequence,
    typing.Tuple,
    typing.Type,
    typing.TypedDict,
    typing.TypeVar,
    typing.Union,
)


def isTypehint(obj):
    if hasattr(obj, "__origin__"):
        obj = obj.__origin__

    if obj in TYPING_TYPES:
        return True

    return inspect.isclass(obj)


def getOrigin(obj):
    """Return obj.__origin__ if it has it else return obj"""
    if hasattr(obj, "__origin__"):
        obj = obj.__origin__
    return obj