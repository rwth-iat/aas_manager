import inspect
import re
from abc import ABCMeta
from enum import Enum
from typing import List, Tuple, Union, Dict, Type

from PyQt5.QtCore import Qt, QFile, QTextStream, QModelIndex
from PyQt5.QtWidgets import QApplication
from aas.model import SubmodelElement, DataElement, SubmodelElementCollection, Event, Constraint

from .settings import ATTR_ORDER, PREFERED_LANGS_ORDER, ATTRS_NOT_IN_DETAILED_INFO, \
    ATTR_INFOS_TO_SIMPLIFY, THEMES


def nameIsSpecial(method_name):
    """Returns true if the method name starts with underscore"""
    return method_name.startswith('_')


def getAttrs(obj, exclSpecial=True, exclCallable=True):
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
    attrs[:] = [attr for attr in attrs if attr not in ATTRS_NOT_IN_DETAILED_INFO]
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


def getDescription(descriptions: dict) -> str:
    if descriptions:
        for lang in PREFERED_LANGS_ORDER:
            if lang in descriptions:
                return descriptions.get(lang)
        return tuple(descriptions.values())[0]


def getReqParams4init(objType:Type, rmDefParams:bool=True, attrsToHide: dict = None) -> Dict[str, Type]:
    """Return required params for init with their type"""
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

    if rmDefParams and defaults:
        for i in range(len(defaults)):
            params.popitem()

    try:
        params.pop('return')
    except KeyError:
        pass

    for param in params:
        if isOptional(params[param]):
            args = list(params[param].__args__)
            args.remove(None.__class__)
            params[param] = args[0]

    if attrsToHide:
        for attr in attrsToHide:
            params.pop(attr)

    return params


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


def isMeta(typ):# todo reimplement if in pyi40aas abstract classes will be really abstract
    if typ in (SubmodelElement, DataElement, SubmodelElementCollection, Event, Constraint):
        return True
    if inspect.isabstract(typ):
        return True
    return False


def issubtype(typ, types: Union[type, Tuple[Union[type, tuple], ...]]) -> bool:
    try:
        if isUnion(typ):
            return any(isUnion(typ) for typ in types)
    except TypeError:
        return isUnion(types)

    if isUnion(types):
        return isUnion(typ)

    if isOptional(typ):
        typ1, typ2 = typ.__args__
        typ = typ1 if typ2 is type(None) else typ2

    try:
        return issubclass(typ, types)
    except TypeError:
        return issubclass(typ.__origin__, types)

# def issubtype(typ, types: Union[type, Tuple[Union[type, tuple], ...]]) -> bool:# todo check if gorg is ok in other versions of python
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


def getAttrTypeHint(objType, attr):
    params = getReqParams4init(objType, rmDefParams=False)
    try:
        return params[attr]
    except KeyError:
        return params[f"{attr}_"]


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
            return doc
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


def getTreeItemPath(treeItem: QModelIndex) -> str:
    path = treeItem.data(Qt.DisplayRole)
    while treeItem.parent().isValid():
        treeItem = treeItem.parent()
        path = f"{treeItem.data(Qt.DisplayRole)}/{path}"
    return path


def toggleTheme(theme: str) -> None:
    if theme in THEMES:
        toggleStylesheet(THEMES[theme])


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
    file = QFile(path)
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())
