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
import typing
from abc import ABCMeta
from enum import Enum
from typing import List, Dict, Type, Set, Any, Tuple, Iterable

from PyQt6.QtCore import Qt, QFile, QTextStream, QModelIndex
from PyQt6.QtWidgets import QApplication
from basyx.aas.model import NamespaceSet, Namespace, Reference

from aas_editor import settings
import aas_editor.utils.util_classes as util_classes
import aas_editor.utils.util_type as util_type
import logging


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
    params = getParams4init(cls)
    attrs = convertParams2Attrs(params, cls)
    attrs = removeHiddenAttrs(attrs, cls)
    return attrs


def convertParams2Attrs(params: List[str], cls) -> List[str]:
    """Convert params to attrs"""
    params_to_attrs = util_classes.ClassesInfo.paramsToAttrs(cls)
    attrs = params.copy()
    for param, attr in params_to_attrs.items():
        try:
            attrs.remove(param)
            attrs.append(attr)
        except ValueError:
            logging.info(f"Attribute {param} not found in {cls}")
    return attrs


def removeHiddenAttrs(attrs: List[str], cls) -> List[str]:
    """Remove hidden attrs from attrs"""
    hidden_attrs = util_classes.ClassesInfo.hiddenAttrs(cls)
    for hidden_attr in hidden_attrs:
        try:
            attrs.remove(hidden_attr)
        except ValueError:
            logging.info(f"Attribute {hidden_attr} not found in {cls}")
    return attrs


def simplifyInfo(obj, attrName: str = "") -> str:
    res = str(obj)
    try:
        if isinstance(obj, settings.ATTR_INFOS_TO_SIMPLIFY):
            res = re.sub("^[A-Z]\w*[(]", "", res)
            res = res.rstrip(")")
        elif issubclass(type(obj), Reference):
            lastKey = obj.key[-1]
            res = f"{lastKey.value} - {lastKey.type.name}"
        elif issubclass(type(obj), NamespaceSet):
            res = f"{{{str([i for i in obj]).strip('[]')}}}"
        elif inspect.isclass(obj):
            res = util_type.getTypeName(obj)
        elif isinstance(obj, Enum):
            res = obj.name
        elif isinstance(obj, dict) and attrName == "description":
            res = getDescription(obj)
        elif res.startswith("<") and res.endswith(">"):  # if no repr for obj
            return ""
    except Exception:
        return str(obj)
    return res


def getLimitStr(obj, max_sgns=settings.MAX_SIGNS_TO_SHOW) -> str:
    try:
        if len(obj) > max_sgns:
            return f"{str(obj)[0:max_sgns]}..."
    except Exception as e:
        logging.exception(e)
    return str(obj)


def getDescription(descriptions: dict) -> str:
    if descriptions:
        for lang in settings.PREFERRED_LANGS_ORDER:
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
    paramsTypehints, paramsDefaults = getParamsAndTypehints4init(objType)
    try:
        return paramsDefaults[param]
    except KeyError:
        if default == settings.NOT_GIVEN:
            raise AttributeError("No such default parameter found:", param)
        else:
            return default


def getParams4init(objType: Type) -> List[str]:
    """Return params for init"""
    objType = resolveBaseType(objType)
    g = getfullargspecoftypeinit(objType)
    paramsAndTypehints = g.annotations.copy()
    if "return" in paramsAndTypehints:
        paramsAndTypehints.pop("return")
    return list(paramsAndTypehints.keys())


def getParamsAndTypehints4init(objType: Type, withDefaults=True) -> tuple[dict[str, Any], dict[str, Any]] | dict[
    str, Any]:
    """Return params for init with their type and default values"""
    objType = resolveBaseType(objType)

    g = getfullargspecoftypeinit(objType)
    paramsAndTypehints = g.annotations.copy()
    if 'return' in paramsAndTypehints:
        paramsAndTypehints.pop('return')
    paramsAndTypehints = replaceForwardRefsWithTypes(paramsAndTypehints)

    if withDefaults:
        defaults = g.defaults
        paramsDefaults = _getDefaultValuesOfParams(paramsAndTypehints.keys(), defaults)
        return paramsAndTypehints, paramsDefaults

    return paramsAndTypehints


def resolveBaseType(objType: Type) -> Type:
    origin = typing.get_origin(objType)
    return origin if origin else objType


def getfullargspecoftypeinit(objType: Type) -> inspect.FullArgSpec:
    if not (hasattr(objType, "__init__") or hasattr(objType, "__new__")):
        raise TypeError(f"no init or new func in objectType: {objType}")

    if hasattr(objType, "__init__"):
        g = inspect.getfullargspec(objType.__init__)
        if hasattr(objType, "__new__") and not g.annotations:
            g = inspect.getfullargspec(objType.__new__)
    else:
        raise TypeError(f"no init or new func in objectType: {objType}")

    if g.kwonlydefaults:
        g.defaults = g.defaults + tuple(g.kwonlydefaults.values())
    return g


def replaceForwardRefsWithTypes(paramsTypehints: Dict[str, Any]) -> Dict[str, Any]:
    for param in paramsTypehints:
        typeHint = paramsTypehints[param]
        paramsTypehints[param] = resolveForwardRef(typeHint)
    return paramsTypehints


def resolveForwardRef(typeHint: Any) -> Any:
    origin = typing.get_origin(typeHint)
    args = typing.get_args(typeHint)

    if origin is None and not args:
        # It's neither a generic type nor a Union
        if type(typeHint) is typing.ForwardRef:
            fullReferencedTypeName = typeHint.__forward_arg__
            referencedTypeName = fullReferencedTypeName.split(".")[-1]
            typeHint = settings.AAS_CLASSES[referencedTypeName]
        return typeHint

    # Replace ForwardRefs in the arguments
    new_args = tuple(resolveForwardRef(arg) for arg in args)

    if origin:
        # Reconstruct generic types like Optional or Tuple
        return origin[new_args]
    else:
        raise TypeError(f"no origin in typeHint, only args: {typeHint}")


def _getDefaultValuesOfParams(params: Iterable[str], defaults: Tuple[Any]) -> Dict[str, Any]:
    params = list(params)
    paramsDefaults = {}
    if params and defaults:
        paramsWithDefaults = params[len(params) - len(defaults):]
        paramsDefaults = dict(zip(paramsWithDefaults, defaults))
    return paramsDefaults


def getReqParams4init(objType: Type, rmDefParams=True,
                      attrsToHide=None, delOptional=True) -> Dict[str, Type]:
    """Return required params for init with their type"""
    paramsTypehints, paramsDefaults = getParamsAndTypehints4init(objType)

    if rmDefParams and paramsDefaults:
        for i in range(len(paramsDefaults)):
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


def _actualizeParents(aasObj, parent=None):
    if hasattr(aasObj, "parent"):
        aasObj.parent = parent
    if isinstance(aasObj, Namespace):
        for namespaceset in aasObj.namespace_element_sets:
            namespaceset.parent = aasObj
            for element in namespaceset:
                _actualizeParents(element, aasObj)

def actualizeAASParents(aasObj):  # TODO change if aas changes
    _actualizeParents(aasObj)

def delAASParent(aasObj):  # TODO change if aas changes
    if hasattr(aasObj, "parent"):
        aasObj.parent = None
    if isinstance(aasObj, NamespaceSet):
        for element in aasObj:
            element.parent = None
    return aasObj

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


def getTreeItemPath(index: QModelIndex, role=Qt.ItemDataRole.DisplayRole, separator="/") -> str:
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
        row += index.row() + 1
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
