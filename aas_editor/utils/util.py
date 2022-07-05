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
import re
from abc import ABCMeta
from enum import Enum
from typing import List, Dict, Type, Set, Any, Tuple

from PyQt5.QtCore import Qt, QFile, QTextStream, QModelIndex
from PyQt5.QtWidgets import QApplication

from aas_editor import settings
import aas_editor.utils.util_classes as util_classes
import aas_editor.utils.util_type as util_type


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
    if attr in settings.ATTR_ORDER:
        return settings.ATTR_ORDER.index(attr)
    return 1000


def getAttrs4detailInfo(obj, exclSpecial: bool = True, exclCallable: bool = True) -> List[str]:
    attrs = getAttrs(obj, exclSpecial, exclCallable)
    for attr in util_classes.ClassesInfo.hiddenAttrs(type(obj)):
        try:
            attrs.remove(attr)
        except ValueError:
            continue
    attrs.sort(key=attrOrder)
    return attrs


def getAttrs4inheritors(cls) -> Set[str]:
    """Return attributes of all inheritor classes of the cls"""
    referableClasses = inheritors(cls)
    aas_attrs = set()
    for cls in referableClasses:
        attrs = getAttrsOfCls(cls)
        aas_attrs.update(attrs)
    return aas_attrs


def getAttrsOfCls(cls) -> Set[str]:
    """Return attributes of the class instance"""
    attrs = list(getParams4init(cls, withDefaults=False).keys())
    params_to_attrs = util_classes.ClassesInfo.params_to_attrs(cls)
    for param, attr in params_to_attrs.items():
        try:
            attrs.remove(param)
            attrs.append(attr)
        except ValueError:
            print("Error occurred while replacing param to attr: probably CLASSES_INFO is corrupted")
    hidden_attrs = util_classes.ClassesInfo.hiddenAttrs(cls)
    for hidden_attr in hidden_attrs:
        try:
            attrs.remove(hidden_attr)
        except ValueError:
            print("Error occurred while removing hidden attr: probably CLASSES_INFO is corrupted")
    return attrs



def simplifyInfo(obj, attrName: str = "") -> str:
    res = str(obj)
    if isinstance(obj, settings.ATTR_INFOS_TO_SIMPLIFY):
        res = re.sub("^[A-Z]\w*[(]", "", res)
        res = res.rstrip(")")
    elif inspect.isclass(obj):
        res = util_type.getTypeName(obj)
    elif isinstance(obj, Enum):
        res = obj.name
    elif isinstance(obj, dict) and attrName == "description":
        res = getDescription(obj)
    elif res.startswith("<") and res.endswith(">"):  # if no repr for obj
        return ""
    return res


def getLimitStr(obj, max_sgns=settings.MAX_SIGNS_TO_SHOW) -> str:
    try:
        if len(obj) > max_sgns:
            return f"{str(obj)[0:max_sgns]}..."
    except Exception as e:
        print(e)
    return str(obj)


def getDescription(descriptions: dict) -> str:
    if descriptions:
        for lang in settings.PREFERED_LANGS_ORDER:
            if lang in descriptions:
                return descriptions.get(lang)
        return tuple(descriptions.values())[0]


def getDefaultVal(objType: Type, param: str, default=settings.NOT_GIVEN):
    """
    :param objType: type
    :param param: name of argument in __init__ or __new__
    :param default: value to return if nothing found
    :raise AttributeError if no default value found and default is not given
    :return: default value for the given attribute for type init
    """
    paramsTypehints, paramsDefaults = getParams4init(objType)
    try:
        return paramsDefaults[param]
    except KeyError:
        if default == settings.NOT_GIVEN:
            raise AttributeError("No such default parameter found:", param)
        else:
            return default


def getParams4init(objType: Type, withDefaults=True):
    """Return params for init with their type and default values"""
    if hasattr(objType, "__origin__") and objType.__origin__:
        objType = objType.__origin__

    if hasattr(objType, "_field_types"):
        # for NamedTuple
        paramsTypehints = objType._field_types.copy()
        defaults = objType._field_defaults if hasattr(objType, "_field_defaults") else {}
    elif hasattr(objType, "__init__") or hasattr(objType, "__new__"):
        if hasattr(objType, "__init__"):
            g = inspect.getfullargspec(objType.__init__)
            paramsTypehints = g.annotations.copy()
            defaults = g.defaults
        if not paramsTypehints and hasattr(objType, "__new__"):
            g = inspect.getfullargspec(objType.__new__)
            paramsTypehints = g.annotations.copy()
            defaults = g.defaults
        if g.kwonlydefaults:
            defaults = defaults + tuple(g.kwonlydefaults.values())
    else:
        raise TypeError(f"no init or new func in objectType: {objType}")

    try:
        paramsTypehints.pop('return')
    except KeyError:
        pass

    if withDefaults:
        paramsDefaults = _getParamsDefaults(paramsTypehints, defaults)
        return paramsTypehints, paramsDefaults
    else:
        return paramsTypehints


def _getParamsDefaults(paramsTypehints: Dict[str, Any], defaults: Tuple[Any]) -> Dict[str, Any]:
    if paramsTypehints and defaults:
        prms = list(paramsTypehints.keys())[len(paramsTypehints) - len(defaults):]
        paramsDefaults = dict(zip(prms, defaults))
    else:
        paramsDefaults = {}
    return paramsDefaults


def getReqParams4init(objType: Type, rmDefParams=True,
                      attrsToHide: dict = None, delOptional=True) -> Dict[str, Type]:
    """Return required params for init with their type"""
    paramsTypehints, paramasDefaults = getParams4init(objType)

    if rmDefParams and paramasDefaults:
        for i in range(len(paramasDefaults)):
            paramsTypehints.popitem()

    if delOptional:
        for param in paramsTypehints:
            typeHint = paramsTypehints[param]
            paramsTypehints[param] = util_type.removeOptional(typeHint)

    if attrsToHide:
        for attr in attrsToHide:
            try:
                paramsTypehints.pop(attr)
            except KeyError:
                continue

    return paramsTypehints


def delAASParents(aasObj): #TODO change if aas changes
    paramsTypehints = getParams4init(type(aasObj), withDefaults=False)

    if hasattr(aasObj, "parent"):
       aasObj.parent = None

    for param in paramsTypehints.keys():
        if hasattr(aasObj, param.rstrip("_")):
            attr = getattr(aasObj, param.rstrip("_"))
        elif hasattr(aasObj, param):
            attr = getattr(aasObj, param)
        else:
            continue

        if hasattr(attr, "parent"):
            attr.parent = None
        if util_type.isIterable(attr):
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

def getDoc(typ: type) -> str:
    return typ.__doc__


def getAttrDoc(attr: str, parentObj: type = None, doc: str = None) -> str:
    """
    Returns doc of specified parameter
    :param attr: parameter of obj init
    :param parentObj: if no doc is given, doc will be extracted from typ
    :param doc: doc of obj init
    :return: doc of specified parameter
    """
    if not doc and parentObj:
        doc = getDoc(parentObj)

    if doc:
        doc = " ".join(doc.split())
        pattern = fr":ivar [~]?[.]?{attr}_?:(.*?)(:ivar|:raises|TODO|$)"
        res = re.search(pattern, doc)
        if res:
            reg = res.regs[1]
            doc = doc[reg[0]: reg[1]]
            doc = re.sub("([(]inherited from.*[)])?", "", doc)
            doc = re.sub("[~]([a-zA-Z]+\.)+", "", doc)
            doc = re.sub("(:class:)?", "", doc)
            doc = re.sub("(<.*>)?", "", doc)
            doc = re.sub("`", "", doc)
            doc = re.sub("[~]\.", "", doc)
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
