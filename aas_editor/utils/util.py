import inspect
import re
from abc import ABCMeta
from enum import Enum
from typing import List, Dict, Type

from PyQt5.QtCore import Qt, QFile, QTextStream, QModelIndex
from PyQt5.QtWidgets import QApplication

from aas_editor.utils.util_classes import ClassesInfo
from aas_editor.settings.aas_settings import ATTR_ORDER, PREFERED_LANGS_ORDER, \
    ATTR_INFOS_TO_SIMPLIFY
from aas_editor.utils.util_type import removeOptional, isIterable, getTypeName


def nameIsSpecial(method_name):
    """Returns true if the method name starts with underscore"""
    return method_name.startswith('_')


def getAttrs(obj, exclSpecial=True, exclCallable=True) -> List[str]:
    attrs: List[str] = dir(obj)
    if exclSpecial:
        attrs[:] = [attr for attr in attrs if not nameIsSpecial(attr)]
    if exclCallable:
        attrs[:] = [attr for attr in attrs
                    if type(getattr(obj, attr)) in (type, ABCMeta)
                    or not callable(getattr(obj, attr))]
    return attrs


def attrOrder(attr):
    if attr in ATTR_ORDER:
        return ATTR_ORDER.index(attr)
    return 1000


def getAttrs4detailInfo(obj, exclSpecial: bool = True, exclCallable: bool = True) -> List[str]:
    attrs = getAttrs(obj, exclSpecial, exclCallable)
    for attr in ClassesInfo.hiddenAttrs(type(obj)):
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
    elif inspect.isclass(obj):
        res = getTypeName(obj)
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
