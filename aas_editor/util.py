import re
from enum import Enum

from .settings import ATTR_ORDER, PREFERED_LANGS_ORDER, ATTRS_NOT_IN_DETAILED_INFO, \
    ATTR_INFOS_TO_SIMPLIFY


def nameIsSpecial(method_name):
    "Returns true if the method name starts with underscore"
    return method_name.startswith('_')


def getAttrs(obj, excludeSpecial=True, excludeCallable=True):
    attrs = dir(obj)
    if excludeSpecial:
        attrs[:] = [attr for attr in attrs if not nameIsSpecial(attr)]
    if excludeCallable:
        attrs[:] = [attr for attr in attrs if not callable(getattr(obj, attr))]
    return attrs


def attrOrder(attr):
    if attr in ATTR_ORDER:
        return ATTR_ORDER.index(attr)
    return 1000


def getAttrs4detailInfo(obj, excludeSpecial=True, excludeCallable=True):
    attrs = getAttrs(obj, excludeSpecial, excludeCallable)
    attrs[:] = [attr for attr in attrs if attr not in ATTRS_NOT_IN_DETAILED_INFO]
    attrs.sort(key=attrOrder)
    return attrs


def simplifyInfo(obj, attr_name=None):
    res = str(obj)
    if isinstance(obj, ATTR_INFOS_TO_SIMPLIFY):
        res = re.sub("^[A-Z]\w*[(]", "", res)
        res = res.rstrip(")")
    elif isinstance(obj, Enum):
        res = re.sub("^[A-Z]\w*[.]", "", res)
    elif isinstance(obj, dict) and attr_name == "description":
        res = getDescription(obj)
    return res


def getDescription(descriptions: dict) -> str:
    if descriptions:
        for lang in PREFERED_LANGS_ORDER:
            if lang in descriptions:
                return descriptions.get(lang)
        return tuple(descriptions.values())[0]

def getAttrDescription(attr: str, docString: str) -> str:
    pattern = fr":param {attr}_?:(.*)"
    res = re.search(pattern, docString)
    if res:
        reg = res.regs[1]
        return docString[reg[0]: reg[1]]
    else:
        return ""
