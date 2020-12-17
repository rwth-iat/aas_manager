import datetime
import decimal
import typing
from enum import Enum
from typing import List, Optional, Set, Type, Union, Dict, TypeVar
from unittest import TestCase

import aas
import dateutil
from aas.model import AASReference, Reference, Submodel, IdentifierType, Referable

from aas_editor.utils.util_type import checkType, issubtype, isoftype


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
        self.assertTrue(issubtype(str, typing.Type[typing.Union[
            dateutil.relativedelta.relativedelta, datetime.datetime, aas.model.datatypes.Date,
            datetime.time, aas.model.datatypes.GYearMonth, aas.model.datatypes.GYear,
            aas.model.datatypes.GMonthDay, aas.model.datatypes.GMonth, aas.model.datatypes.GDay,
            bool, aas.model.datatypes.Base64Binary, aas.model.datatypes.HexBinary,
            aas.model.datatypes.Float, float, decimal.Decimal, int, aas.model.datatypes.Long,
            aas.model.datatypes.Int, aas.model.datatypes.Short, aas.model.datatypes.Byte,
            aas.model.datatypes.NonPositiveInteger, aas.model.datatypes.NegativeInteger,
            aas.model.datatypes.NonNegativeInteger, aas.model.datatypes.PositiveInteger,
            aas.model.datatypes.UnsignedLong, aas.model.datatypes.UnsignedInt,
            aas.model.datatypes.UnsignedShort, aas.model.datatypes.UnsignedByte,
            aas.model.datatypes.AnyURI, str, aas.model.datatypes.NormalizedString]]))

        self.assertFalse(issubtype(list, Set[str]))
        self.assertFalse(issubtype(AASReference, Submodel))
        self.assertFalse(issubtype(Submodel, AASReference[str]))
        self.assertFalse(issubtype(Submodel, Union[int, float, str]))
        self.assertFalse(issubtype(str, Union))
        self.assertFalse(issubtype(str, Type))

        self.assertFalse(issubtype(int, (float, str)))

    def test_isoftype(self):
        self.assertTrue(isoftype(2, int))
        self.assertTrue(isoftype([1,2], List))
        self.assertTrue(isoftype([1,2], List[int]))
        self.assertTrue(isoftype({1:2}, Dict[int, str]))
        self.assertTrue(isoftype({1:2}, Dict))
        self.assertTrue(isoftype(str, Type[str]))
        self.assertTrue(isoftype(float, Type[Union[int, float, str]]))
        _RT = TypeVar('_RT', bound=Referable)
        self.assertTrue(isoftype(Submodel, _RT))

        self.assertFalse(isoftype("gfvds", Set[str]))
        self.assertFalse(isoftype({1,2}, Union[int, float, str]))
        self.assertFalse(isoftype("xsdgvfdv", Type[str]))
        self.assertFalse(isoftype(45.3, Type[Union[int, float, str]]))

    def test_checkType(self):
        Nonetype = type(None)
        test_set={
            "dsgf":str,
            None:Union[str, Nonetype],
            {2:3}:Union[Dict[str, str], Nonetype]
        }
        for typ in test_set:
            typeHint = test_set[typ]
            print("Check", typeHint, type)
            self.assertTrue(checkType(typ, typeHint))