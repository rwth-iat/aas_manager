from enum import Enum
from typing import List, Optional, Set, Type, Union, Dict, TypeVar
from unittest import TestCase

from aas.model import AASReference, Reference, Submodel, IdentifierType, Referable

from aas_editor.util import issubtype, isoftype


class TestUtilFuncs(TestCase):
    def test_issubtype(self):
        self.assertTrue(issubtype(int, int))
        self.assertTrue(issubtype(AASReference, AASReference))
        self.assertTrue(issubtype(AASReference, Reference))
        self.assertTrue(issubtype(AASReference, AASReference[str]))
        self.assertTrue(issubtype(list, List[int]))
        self.assertTrue(issubtype(list, Optional[List[int]]))
        self.assertTrue(issubtype(Type, Type))
        self.assertTrue(issubtype(str, Type[str]))
        self.assertTrue(issubtype(str, Type[Union[int, float, str]]))
        self.assertTrue(issubtype(float, Union[int, float, str]))
        self.assertTrue(issubtype(IdentifierType, Enum))

        self.assertTrue(issubtype(int, (int, str)))
        self.assertTrue(issubtype(list, (set, List[int])))
        self.assertTrue(issubtype(list, Optional[List[int]]))
        self.assertTrue(issubtype(IdentifierType, (bool, str, int, float, Enum, Type)))

        self.assertFalse(issubtype(list, Set[str]))
        self.assertFalse(issubtype(AASReference, Submodel))
        self.assertFalse(issubtype(Submodel, AASReference[str]))
        self.assertFalse(issubtype(Submodel, Union[int, float, str]))
        self.assertFalse(issubtype(str, Union))
        self.assertTrue(issubtype(str, Type))

        self.assertFalse(issubtype(int, (float, str)))

    def test_isoftype(self):
        self.assertTrue(isoftype(2, int))
        self.assertTrue(isoftype([1,2], List))
        self.assertTrue(isoftype([1,2], List[int]))
        self.assertTrue(isoftype({1:2}, Dict[int, str]))
        self.assertTrue(isoftype({1:2}, Dict))
        self.assertTrue(isoftype("xsdgvfdv", Type[str]))
        self.assertTrue(isoftype(45.3, Type[Union[int, float, str]]))
        _RT = TypeVar('_RT', bound=Referable)
        self.assertTrue(isoftype(Submodel, _RT))

        self.assertFalse(isoftype("gfvds", Set[str]))
        self.assertFalse(isoftype({1,2}, Union[int, float, str]))
