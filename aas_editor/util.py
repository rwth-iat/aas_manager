import inspect
import re
import typing
from enum import Enum
from typing import List

from PyQt5.QtCore import Qt, QFile, QTextStream, QModelIndex
from PyQt5.QtWidgets import QApplication

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
        res = re.sub("^[A-Z]\w*[.]", "", res)
    elif isinstance(obj, dict) and attrName == "description":
        res = getDescription(obj)
    return res


def getDescription(descriptions: dict) -> str:
    if descriptions:
        for lang in PREFERED_LANGS_ORDER:
            if lang in descriptions:
                return descriptions.get(lang)
        return tuple(descriptions.values())[0]


def getReqParams4init(objType, rmDefaultAttrs=True) -> dict:
    """Return required params for init with their type"""
    g = inspect.getfullargspec(objType.__init__)
    params = g.annotations.copy()

    if rmDefaultAttrs and g.defaults:
        for i in range(len(g.defaults)):
            params.popitem()

    try:
        params.pop('return')
    except KeyError:
        pass

    for param in params:
        if _isOptional(params[param]):
            args = list(params[param].__args__)
            args.remove(None.__class__)
            params[param] = args[0]

    return params


def _isOptional(param):
    if param.__class__ == typing.Union.__class__ and \
            None.__class__ in param.__args__ and \
            len(param.__args__) == 2:
        return True
    return False


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
