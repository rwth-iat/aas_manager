from typing import NamedTuple, Any, Type, Tuple

from aas_editor.settings.util_constants import *
from aas_editor.settings import aas_settings as s


# DictItem = NamedTuple("DictItem", key=Any, value=Any)
class DictItem(NamedTuple):
    key: Any
    value: Any

    @property
    def name(self):
        return self.key

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"{self.key}: {self.value}"


class ClassesInfo:
    # @staticmethod
    # @property
    # def hiddenAttrs() -> Dict[Type, List[str]]:
    #     res = {}
    #     for typ in s.CLASSES_INFO:
    #         try:
    #             res[typ] = s.CLASSES_INFO[typ][s.ATTRS_NOT_IN_DETAILED_INFO]
    #         except KeyError:
    #             continue
    #     return res
    #
    # @staticmethod
    # @property
    # def addActTexts() -> Dict[Type, List[str]]:
    #     res = {}
    #     for typ in s.CLASSES_INFO:
    #         try:
    #             res[typ] = s.CLASSES_INFO[typ][s.ADD_ACT_AAS_TXT]
    #         except KeyError:
    #             continue
    #     return res
    #
    # @staticmethod
    # @property
    # def changedParentObjects() -> Dict[Type, List[str]]:
    #     res = {}
    #     for typ in s.CLASSES_INFO:
    #         try:
    #             res[typ] = s.CLASSES_INFO[typ][s.ADD_ACT_AAS_TXT]
    #         except KeyError:
    #             continue
    #     return res

    @staticmethod
    def hiddenAttrs(cls) -> Tuple[str]:
        res = set()
        for typ in s.CLASSES_INFO:
            if issubclass(cls, typ):
                try:
                    res.update(s.CLASSES_INFO[typ][
                                   HIDDEN_ATTRS])
                except KeyError:
                    continue
        return tuple(res)

    @staticmethod
    def addActText(cls) -> str:
        clsInfo = s.CLASSES_INFO.get(cls, {})
        res = clsInfo.get(ADD_ACT_AAS_TXT, "")
        if not res:
            for typ in s.CLASSES_INFO:
                if issubclass(cls, typ):
                    try:
                        res = s.CLASSES_INFO[typ][
                            ADD_ACT_AAS_TXT]
                        return res
                    except KeyError:
                        continue
        return res

    @staticmethod
    def changedParentObject(cls) -> str:
        clsInfo = s.CLASSES_INFO.get(cls, {})
        res = clsInfo.get(CHANGED_PARENT_OBJ, "")
        if not res:
            for typ in s.CLASSES_INFO:
                if issubclass(cls, typ):
                    try:
                        res = s.CLASSES_INFO[typ][
                            CHANGED_PARENT_OBJ]
                        return res
                    except KeyError:
                        continue
        return res

    @staticmethod
    def addType(cls) -> Type:
        clsInfo = s.CLASSES_INFO.get(cls, {})
        res = clsInfo.get(ADD_TYPE, None)
        if not res:
            for typ in s.CLASSES_INFO:
                if issubclass(cls, typ):
                    try:
                        res = s.CLASSES_INFO[typ][ADD_TYPE]
                        return res
                    except KeyError:
                        continue
        return res
