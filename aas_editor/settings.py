from enum import Enum
from pathlib import Path

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QKeySequence, QColor, QFont
from aas.model import *
# from aas.model import AdministrativeInformation, Identifier, Submodel, AASReference, Asset, \
#     SubmodelElement, AssetAdministrationShell, ConceptDescription, AbstractObjectStore, Event, \
#     AnnotatedRelationshipElement, RelationshipElement, Operation, \
#     SubmodelElementCollectionUnordered, SubmodelElementCollectionOrdered, Entity, Capability, \
#     Property

AAS_CREATOR = "PyI40AAS Testing Framework"

ATTR_COLUMN_WIDTH = 200

DEFAULT_MAINWINDOW_SIZE = QSize(1194, 624)
MAX_FONT_SIZE = 60
MIN_FONT_SIZE = 6
DEFAULT_FONT = QFont()
DEFAULT_FONT.setPointSize(12)

# Themes
DEFAULT_THEME = "dark"
DARK_THEME_PATH = "themes/dark.qss"
LIGHT_THEME_PATH = "themes/light.qss"
THEMES = {"dark": DARK_THEME_PATH, "light": LIGHT_THEME_PATH, "standard": ""}

APPLICATION_NAME = "AAS Editor"
ACPLT = "ACPLT"

MAX_RECENT_FILES = 4

PREFERED_LANGS_ORDER = ("en-us", "en", "de")

ATTR_ORDER = (
    "id_short",
    "category",
    "value",
    "in_output_variable",
    "input_variable",
    "output_variable",
    "first",
    "second",
    "kind",
    "entity_type",
    "description",
    "administration",
    "identification",
)

LIGHT_BLUE = QColor(132, 185, 255)
LINK_BLUE = QColor(26, 13, 171)
CHANGED_BLUE = QColor(83, 148, 236, 255)
NEW_GREEN = QColor("green")

PACKAGE_ATTRS = ("shells", "assets", "submodels", "concept_descriptions", "others", "files")
ATTRS_NOT_IN_DETAILED_INFO = ("gi_code",
                              "gi_frame",
                              "gi_running",
                              "gi_yieldfrom",
                              "namespace_element_sets",
                              "parent",
                              "security", #TODO delete when implemented in aas
                              "submodel_element") + PACKAGE_ATTRS
TYPES_NOT_TO_POPULATE = (
    AbstractObjectStore, str, int, float, bool, Enum, Path)  # '+ TYPES_IN_ONE_ROW
ATTRS_IN_PACKAGE_TREEVIEW = PACKAGE_ATTRS
ATTR_INFOS_TO_SIMPLIFY = (AdministrativeInformation, Identifier,)
LINK_TYPES = (
    AASReference,
    Submodel,
    Asset,
    SubmodelElement,
    AssetAdministrationShell,
    ConceptDescription,
)

DEFAULT_ATTRS_TO_HIDE = {"parent": None}
PACKAGE_ROLE = 1001
NAME_ROLE = 1002
OBJECT_ROLE = 1003
PACK_ITEM_ROLE = 1004
LINKED_ITEM_ROLE = 1005
IS_LINK_ROLE = 1006
COLUMNS_IN_DETAILED_INFO = ("attribute", "value")
ATTRIBUTE_COLUMN = 0
VALUE_COLUMN = 1

NOT_GIVEN = "NotGivenValueAASEditor"

# Shortcuts
SC_COPY = QKeySequence.Copy
SC_CUT = QKeySequence.Cut
SC_PASTE = QKeySequence.Paste
SC_DELETE = QKeySequence.Delete
SC_NEW = QKeySequence.New

SC_ZOOM_IN = QKeySequence(Qt.CTRL + Qt.Key_Plus)
SC_ZOOM_OUT = QKeySequence(Qt.CTRL + Qt.Key_Minus)

SC_EXPAND_RECURS = QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_Plus)
SC_EXPAND_ALL = QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Plus)
SC_COLLAPSE_RECURS = QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_Minus)
SC_COLLAPSE_ALL = QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Minus)

SC_OPEN = QKeySequence(Qt.CTRL + Qt.Key_O)
SC_SAVE_ALL = QKeySequence(Qt.CTRL + Qt.Key_S)
SC_BACK = QKeySequence.Back
SC_FORWARD = QKeySequence.Forward

SC_FOCUS2RIGTH_TREE = QKeySequence(Qt.CTRL + Qt.RightArrow)
SC_FOCUS2LEFT_TREE = QKeySequence(Qt.CTRL + Qt.LeftArrow)

import qtawesome as qta

ICON_DEFAULTS = {'scale_factor': 1.2,
                 'color': QColor(LIGHT_BLUE.red(), LIGHT_BLUE.green(), LIGHT_BLUE.blue(), 225),
                 'color_active': QColor(LIGHT_BLUE.red(), LIGHT_BLUE.green(), LIGHT_BLUE.blue(),
                                        255),
                 'color_disabled': QColor(LIGHT_BLUE.red(), LIGHT_BLUE.green(), LIGHT_BLUE.blue(),
                                          50), }
ELEM_ICON_DEFAULTS = {'scale_factor': 1.6,
                      'color': QColor(LIGHT_BLUE.red(), LIGHT_BLUE.green(), LIGHT_BLUE.blue(), 255)}

qta.set_defaults(**ICON_DEFAULTS)

EXIT_ICON = qta.icon("mdi.exit-to-app")
OPEN_ICON = qta.icon("mdi.folder-open")
SAVE_ICON = qta.icon("mdi.content-save")
SAVE_ALL_ICON = qta.icon("mdi.content-save-all")

COPY_ICON = qta.icon("mdi.content-copy")
PASTE_ICON = qta.icon("mdi.content-paste")
CUT_ICON = qta.icon("mdi.content-cut")
ADD_ICON = qta.icon("mdi.plus-circle")
DEL_ICON = qta.icon("mdi.delete")

FORWARD_ICON = qta.icon("fa5s.arrow-circle-right")
BACK_ICON = qta.icon("fa5s.arrow-circle-left")

SPLIT_VERT_ICON = qta.icon("mdi.arrow-split-horizontal")
SPLIT_HORIZ_ICON = qta.icon("mdi.arrow-split-vertical")

ZOOM_IN_ICON = qta.icon("mdi.magnify-plus")
ZOOM_OUT_ICON = qta.icon("mdi.magnify-minus")


# CHARS4=[{'offset': (-0.48, 0)}, {'offset': (-0.16, 0)},
#         {'offset': (0.15, 0)}, {'offset': (0.46, 0)}]
CHARS1_3=[{'offset': (-0.48, 0)}, {'offset': (-0.13, 0)},
         {'offset': (0.18, 0)}, {'offset': (0.48, 0)}]
# CHARS3=[{'offset': (-0.3, 0)}, {'offset': (0, 0)}, {'offset': (0.3, 0)}]
CHARS3=[{'offset': (-0.48, 0)}, {'offset': (0, 0)}, {'offset': (0.48, 0)}]
CHARS4=[{'offset': (-0.54, 0)}, {'offset': (-0.18, 0)},
        {'offset': (0.18, 0)}, {'offset': (0.54, 0)}]
CHARS1_3=CHARS4


def getCharsIcon(chars: str):
    if len(chars) == 3:
        options = CHARS3
    elif len(chars) == 4:
        options = CHARS4

    mdiChar = "mdi.alpha"
    args = []
    for char in chars.lower():
        args.append(f"{mdiChar}-{char}")
    return qta.icon(*args, options=options)

# element icons
qta.set_defaults(**ELEM_ICON_DEFAULTS)
TYPE_ICON_DICT = {
    AssetAdministrationShell: getCharsIcon("shel"),  # qta.icon("mdi.wallet") #  mdi.tab mdi.shredder folder-outline wallet
    Asset: getCharsIcon("asst"),  # qta.icon("mdi.mini-sd") # mdi.toy-brick
    ConceptDescription: getCharsIcon("conc"),  # qta.icon("mdi.text-box")
    Submodel: getCharsIcon("sub"),

    Property: getCharsIcon("prop"),
    Entity: getCharsIcon("ent"),
    Capability: getCharsIcon("cap"),
    Event: getCharsIcon("evnt"),  # qta.icon("mdi.timeline-clock")  # mdi.timer mdi.bell
    Operation: getCharsIcon("oper"),  # qta.icon("mdi.cog")
    RelationshipElement: getCharsIcon("rel"),
    AnnotatedRelationshipElement: getCharsIcon("arel"), # qta.icon("mdi.arrow-left-right")  # mdi.relation-one-to-one
    SubmodelElementCollectionUnordered: getCharsIcon("ucol"),
    SubmodelElementCollectionOrdered: getCharsIcon("ocol"),  # qta.icon("mdi.package")

    Range: getCharsIcon("rnge"),
    Blob: getCharsIcon("blob"),
    File: getCharsIcon("file"),
    ReferenceElement: getCharsIcon("ref"),
    DataElement: getCharsIcon("data"),
}