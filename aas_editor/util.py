import inspect
import re
import typing
from abc import ABCMeta
from enum import Enum
from typing import List, Tuple, Union, Dict, Type, Iterable, ForwardRef
from collections import abc

from PyQt5.QtCore import Qt, QFile, QTextStream, QModelIndex
from PyQt5.QtWidgets import QApplication
from aas.model import AASReference

from aas_editor.util_classes import DictItem
from aas_editor.settings import NAME_ROLE, OBJECT_ROLE, PARENT_OBJ_ROLE
from aas_editor.aas_settings import ATTR_ORDER, PREFERED_LANGS_ORDER, \
    ATTR_INFOS_TO_SIMPLIFY, COMPLEX_ITERABLE_TYPES, CLS_ATTRS_NOT_IN_DETAILED_INFO


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


def nameIsSpecial(method_name):
    """Returns true if the method name starts with underscore"""
    return method_name.startswith('_')


def getAttrs(obj, exclSpecial=True, exclCallable=True) -> List[str]:
    attrs = dir(obj)
    if exclSpecial:
        attrs[:] = [attr for attr in attrs if not nameIsSpecial(attr)]
    if exclCallable:
        attrs[:] = [attr for attr in attrs if not callable(getattr(obj, attr))]
    return attrs


def attrOrder(attr):
    if attr in ATTR_ORDER:
        return ATTR_ORDER.index(attr)
    return 1000


def getAttrs4detailInfo(obj, exclSpecial: bool = True, exclCallable: bool = True) -> List[str]:
    attrs = getAttrs(obj, exclSpecial, exclCallable)
    for cls in CLS_ATTRS_NOT_IN_DETAILED_INFO:
        if isinstance(obj, cls):
            for attr in CLS_ATTRS_NOT_IN_DETAILED_INFO[cls]:
                try:
                    attrs.remove(attr)
                except ValueError:
                    continue
    attrs.sort(key=attrOrder)
    return attrs


def simplifyInfo(obj, attrName: str = "") -> str:
    res = str(obj)
    if isinstance(obj, ATTR_INFOS_TO_SIMPLIFY):
        res = re.sub("^[A-Z]\w*[(]", "", res)
        res = res.rstrip(")")
    elif isinstance(obj, Enum):
        res = obj.name
    elif isinstance(obj, dict) and attrName == "description":
        res = getDescription(obj)
    return res


def getTypeName(objType) -> str:
    try:
        if objType.__name__:
            return objType.__name__
    except AttributeError:
        pass

    try:
        if objType._name:
            return objType._name
    except AttributeError:
        pass

    try:
        if objType.name:
            return objType.name
    except AttributeError:
        name = str(objType)
        # delete args if exist
        name = name.partition("[")[0]
        # delete type parents and return only type name
        return name.rpartition(".")[2]


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


def getDescription(descriptions: dict) -> str:
    if descriptions:
        for lang in PREFERED_LANGS_ORDER:
            if lang in descriptions:
                return descriptions.get(lang)
        return tuple(descriptions.values())[0]


def getDefaultVal(param: str, objType: Type):
    params, defaults = getParams4init(objType)
    if params and defaults:
        params = list(params.keys())
        revParams = reversed(params)
        revDefaults = list(reversed(defaults))
        for n, par in enumerate(revParams):
            if par == param:
                defValue = revDefaults[n]
                return defValue
            elif par.rstrip('_') == param:  # TODO change if aas changes
                defValue = revDefaults[n]
                return defValue

    raise AttributeError("No such default parameter found:", param)


def getParams4init(objType: Type):
    """Return params for init with their type and default values"""
    if hasattr(objType, "__origin__") and objType.__origin__:
        objType = objType.__origin__

    if hasattr(objType, "_field_types"):
        # for NamedTuple
        params = objType._field_types.copy()
        defaults = objType._field_defaults if hasattr(objType, "_field_defaults") else {}
    elif hasattr(objType, "__init__"):
        g = inspect.getfullargspec(objType.__init__)
        params = g.annotations.copy()
        defaults = g.defaults
    elif hasattr(objType, "__new__"):
        g = inspect.getfullargspec(objType.__new__)
        params = g.annotations.copy()
        defaults = g.defaults
    else:
        raise TypeError(f"no init or new func in objectType: {objType}")

    try:
        params.pop('return')
    except KeyError:
        pass

    return params, defaults


def getReqParams4init(objType: Type, rmDefParams=True,
                      attrsToHide: dict = None, delOptional=True) -> Dict[str, Type]:
    """Return required params for init with their type"""
    params, defaults = getParams4init(objType)

    if rmDefParams and defaults:
        for i in range(len(defaults)):
            params.popitem()

    if delOptional:
        for param in params:
            typeHint = params[param]
            params[param] = removeOptional(typeHint)

    if attrsToHide:
        for attr in attrsToHide:
            try:
                params.pop(attr)
            except KeyError:
                continue

    return params


def delAASParents(aasObj): #TODO change if aas changes
    params, defaults = getParams4init(type(aasObj))

    if hasattr(aasObj, "parent"):
       aasObj.parent = None

    for param in params.keys():
        if hasattr(aasObj, param.rstrip("_")):
            attr = getattr(aasObj, param.rstrip("_"))
        elif hasattr(aasObj, param):
            attr = getattr(aasObj, param)
        else:
            continue

        if hasattr(attr, "parent"):
            attr.parent = None
        if isIterable(attr):
            for item in attr:
                if hasattr(item, "parent"):
                    item.parent = None


def isOptional(typeHint):
    if isUnion(typeHint):
        if type(None) in typeHint.__args__:
            if len(typeHint.__args__) == 2:
                return True
    return False


def isUnion(typeHint):
    if hasattr(typeHint, "__origin__"):
        if type(typeHint.__origin__) == type(Union):
            return True
    if type(typeHint) == type(Union):
        return True
    return False


def issubtype(typ, types: Union[type, Tuple[Union[type, tuple], ...]]) -> bool:
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

# todo check if gorg is ok in other versions of python
# def issubtype(typ, types: Union[type, Tuple[Union[type, tuple], ...]]) -> bool:
#     if types == Union:
#         if hasattr(typ, "__origin__") and typ.__origin__:
#             return typ.__origin__ == types
#         if hasattr(typ, "_gorg"):
#             return typ._gorg == types
#         else:
#             return typ == types
#
#     if isinstance(types, typing.Iterable) and typ in types:
#         return True
#     elif typ == types:
#         return True
#     if hasattr(typ, "__origin__") and typ.__origin__:
#         print(typ.__origin__)
#         if typ.__origin__ == typing.Union:
#             if None.__class__ in typ.__args__ and len(typ.__args__) == 2:
#                 args = list(typ.__args__)
#                 args.remove(None.__class__)
#                 typ = args[0]
#                 if hasattr(typ, "__origin__") and typ.__origin__:
#                     typ = typ.__origin__
#                 return issubclass(typ, types)
#             elif isinstance(types, typing.Iterable):
#                 return typ.__origin__ in types
#             else:
#                 return typ.__origin__ == types
#         else:
#             return issubclass(typ.__origin__, types)
#     if hasattr(typ, "_gorg"):
#         return issubclass(typ._gorg, types)
#     return issubclass(typ, types)


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


def getAttrDoc(attr: str, doc: str) -> str:
    """
    Returns doc of specified parameter
    :param attr: parameter of obj init
    :param doc: doc of obj init
    :return: doc of specified parameter
    """
    if doc:
        doc = " ".join(doc.split())
        pattern = fr":param {attr}_?:(.*?)(:param|:raises|TODO|$)"
        res = re.search(pattern, doc)
        if res:
            reg = res.regs[1]
            doc = doc[reg[0]: reg[1]]
            doc = re.sub("([(]from .*[)])?", "", doc)
            doc = f"{attr}: {doc}"
            return doc
    return ""


def richText(text: str):
    if text:
        return f"<html><head/><body><p>{text}</p></body></html>"
    else:
        return ""


def inheritors(klass) -> set:
    """Return all inheritors of the class"""
    subclasses = set()
    work = [klass]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return subclasses


def getTreeItemPath(index: QModelIndex, role=Qt.DisplayRole, separator="/") -> str:
    path = ""
    while index.isValid():
        path = f"{index.data(role)}{separator}{path}"
        index = index.parent()
    return path.rstrip(separator)


def absRow(index: QModelIndex):
    maxChildren = 100
    row = 0
    while index.isValid():
        row /= maxChildren
        row += index.row()+1
        index = index.parent()
    return row


def toggleStylesheet(path: str) -> None:
    """
    Toggle the stylesheet to use the desired path in the Qt resource
    system (prefixed by `:/`) or generically (a path to a file on
    system).

    :path:      A full path to a resource or file on system
    """
    # get the QApplication instance,  or crash if not set
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("No Qt Application found.")
    if path:
        file = QFile(path)
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)
        app.setStyleSheet(stream.readAll())
    else:
        app.setStyleSheet("")
