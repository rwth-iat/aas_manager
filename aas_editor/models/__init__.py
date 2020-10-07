# pyuic5 aas_editor/mainwindow_base.ui -o aas_editor/design.py
from enum import Enum

PACKAGE_ROLE = 1001
NAME_ROLE = 1002
OBJECT_ROLE = 1003

TYPES_NOT_TO_POPULATE = (str, int, float, bool, Enum,)  # '+ TYPES_IN_ONE_ROW

COLUMNS_IN_DETAILED_INFO = ("attribute", "value")
ATTRIBUTE_COLUMN = 0
VALUE_COLUMN = 1

STRING_ATTRS = ("id", "id_short", "category", "version", "revision")
SUBMODEL_ATTRS = ("asset_identification_model", "bill_of_material")

from .package import *
from .item_standard import *
from .item_detailed_info import *
from .item_pack_treeview import *
from .table_standard import *
from .table_detailed_info import *
