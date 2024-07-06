#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/

import datetime
import inspect
from abc import ABCMeta
from enum import Enum
from pathlib import Path

import basyx.aas.model
from basyx.aas.model import AssetAdministrationShell, ConceptDescription, Submodel, Property, \
    Entity, Capability, Operation, RelationshipElement, AnnotatedRelationshipElement, Range, Blob, File, \
    ReferenceElement, DataElement, AdministrativeInformation, AbstractObjectStore, \
    Namespace, SubmodelElementCollection, SubmodelElement, ModelReference, Referable, Identifiable, \
    Key, Qualifier, BasicEventElement, SubmodelElementList, datatypes, LangStringSet, DictObjectStore

import aas_editor.additional.classes
import aas_editor.package
from aas_editor.import_feature import import_util_classes
from aas_editor.settings.util_constants import HIDDEN_ATTRS, CHANGED_PARENT_OBJ, ADD_ACT_AAS_TXT, \
    ADD_TYPE, PACKVIEW_ATTRS_INFO, PARAMS_TO_ATTRS, DEFAULT_PARAMS_TO_HIDE, ITERABLE_ATTRS, POSITIONAL_ARG_DEFAULTS, \
    CONTENT_TYPE_ATTR, CONTENT_VALUE_ATTR, IS_EDITABLE_IN_GUI
from aas_editor.settings.icons import getCharsIcon
from aas_editor.utils import util_type
import aas_editor.utils.util as util

AAS_FILES_FILTER = "AAS files (*.aasx *.xml *.json)"
AASX_FILES_FILTER = "AASX files (*.aasx)"
XML_FILES_FILTER = "XML files (*.xml)"
JSON_FILES_FILTER = "JSON files (*.json)"
ALL_FILES_FILTER = "All files (*.*)"

FILE_TYPES = {
    "json": "json",
    "xml": "xml",
    "aasx": "aasx",
}
FILE_TYPE_FILTERS = {
    "json": JSON_FILES_FILTER,
    "xml": XML_FILES_FILTER,
    "aasx": AASX_FILES_FILTER,
}
FILTER_AAS_FILES = f"{AAS_FILES_FILTER};;{AASX_FILES_FILTER};;{XML_FILES_FILTER};;{JSON_FILES_FILTER};;{ALL_FILES_FILTER}"

EMPTY_VALUES = (None, tuple(), set(), list(), dict())

LINK_TYPES = (ModelReference,)

MEDIA_TYPES_INFOS = {
    File: {
        CONTENT_TYPE_ATTR: "content_type",
        CONTENT_VALUE_ATTR: "value",
    },
    Blob: {
        CONTENT_TYPE_ATTR: "content_type",
        CONTENT_VALUE_ATTR: "value",
    },
    aas_editor.package.StoredFile: {
        CONTENT_TYPE_ATTR: "mime_type",
        CONTENT_VALUE_ATTR: "value",
    }
}

# AnyXSDType = Base64Binary, HexBinary

from basyx.aas import model

TYPE_NAMES_DICT = {
    model.datatypes.String: "String",
    model.datatypes.Boolean: "Boolean",
    model.datatypes.Double: "Double",
    model.datatypes.Decimal: "Decimal",
    int: "Integer",
    model.datatypes.Duration: "Duration",
    model.datatypes.DateTime: "DateTime",
    model.datatypes.Time: "Time",
}

ATTR_ORDER = (
    "id_short",
    "category",
    "value",
    "value_type",
    "in_output_variable",
    "input_variable",
    "output_variable",
    "first",
    "second",
    "kind",
    "entity_type",
    "description",
    "administration",
    "id",
)
PREFERRED_LANGS_ORDER = ("en-us", "en", "de")

CLASSES_INFO = {
    object: {
        HIDDEN_ATTRS: ("namespace_element_sets", "parent", "security", "source"),
    },
    datetime.datetime: {
        HIDDEN_ATTRS: ("min", "max", "resolution"),
    },
    aas_editor.package.Package: {
        HIDDEN_ATTRS: ("ATTRS_INFO", "shells", "assets", "submodels", "concept_descriptions", "others", "fileStore"),
        ADD_ACT_AAS_TXT: "Add package",
        ADD_TYPE: aas_editor.package.Package,
        PACKVIEW_ATTRS_INFO: {
            "shells": {
                ADD_ACT_AAS_TXT: "Add shell",
                ADD_TYPE: AssetAdministrationShell,
            },
            "submodels": {
                ADD_ACT_AAS_TXT: "Add submodel",
                ADD_TYPE: Submodel,
            },
            "concept_descriptions": {
                ADD_ACT_AAS_TXT: "Add concept description",
                ADD_TYPE: ConceptDescription,
            },
            "fileStore": {
                ADD_ACT_AAS_TXT: "Add file",
                ADD_TYPE: aas_editor.package.StoredFile,
            },
        },
        IS_EDITABLE_IN_GUI: False,
    },
    DictObjectStore: {
        IS_EDITABLE_IN_GUI: False,
    },
    Referable: {
        DEFAULT_PARAMS_TO_HIDE: {"parent": None},
        POSITIONAL_ARG_DEFAULTS: {"id_short": None},
    },
    Identifiable: {
        PARAMS_TO_ATTRS: {
            "id_": "id"
        },
    },
    AssetAdministrationShell: {
    },
    Submodel: {
        HIDDEN_ATTRS: ("submodel_element",),
        ITERABLE_ATTRS: ("submodel_element",),
        CHANGED_PARENT_OBJ: "submodel_element",
        ADD_ACT_AAS_TXT: "Add submodel element",
        ADD_TYPE: SubmodelElement,
    },
    AnnotatedRelationshipElement: {
        HIDDEN_ATTRS: ("annotation",),
        ITERABLE_ATTRS: ("annotation",),
        CHANGED_PARENT_OBJ: "annotation",
        ADD_ACT_AAS_TXT: "Add annotation",
        ADD_TYPE: DataElement,
    },
    SubmodelElementCollection: {
        HIDDEN_ATTRS: ("value",),
        ITERABLE_ATTRS: ("value",),
        CHANGED_PARENT_OBJ: "value",
        ADD_ACT_AAS_TXT: "Add submodel element to collection",
        ADD_TYPE: SubmodelElement,
    },
    SubmodelElementList: {
        HIDDEN_ATTRS: ("value",),
        ITERABLE_ATTRS: ("value",),
        CHANGED_PARENT_OBJ: "value",
        ADD_ACT_AAS_TXT: "Add submodel element to list",
        ADD_TYPE: SubmodelElement,
    },
    Entity: {
        HIDDEN_ATTRS: ("statement",),
        ITERABLE_ATTRS: ("statement",),
        CHANGED_PARENT_OBJ: "statement",
        ADD_ACT_AAS_TXT: "Add statement",
        ADD_TYPE: SubmodelElement,
    },
    Operation: {
        HIDDEN_ATTRS: ("input_variable", "output_variable", "in_output_variable"),
        ITERABLE_ATTRS: ("input_variable", "output_variable", "in_output_variable"),
        PACKVIEW_ATTRS_INFO: {
            "input_variable": {
                ADD_ACT_AAS_TXT: "Add input variable",
                ADD_TYPE: SubmodelElement,
            },
            "output_variable": {
                ADD_ACT_AAS_TXT: "Add output variable",
                ADD_TYPE: SubmodelElement,
            },
            "in_output_variable": {
                ADD_ACT_AAS_TXT: "Add in_output variable",
                ADD_TYPE: SubmodelElement,
            },
        }
    },
    ModelReference: {
        PARAMS_TO_ATTRS: {
            "type_": "type"
        },
    },
    Key: {
        PARAMS_TO_ATTRS: {
            "type_": "type"
        },
    },
    Qualifier: {
        PARAMS_TO_ATTRS: {
            "type_": "type"
        },
    },
}

AAS_CLASSES = {name:obj for name, obj in inspect.getmembers(basyx.aas.model) if inspect.isclass(obj)}
EXTENDED_COLUMNS_IN_PACK_TABLE = list(util.getAttrs4inheritors(Referable))
EXTENDED_COLUMNS_IN_PACK_TABLE.sort()
REFERABLE_INHERITORS = sorted(list(util.inheritors(Referable)), key=util_type.getTypeName)

REFERABLE_INHERITORS_ATTRS = {}
for inheritor in REFERABLE_INHERITORS:
    REFERABLE_INHERITORS_ATTRS.update({inheritor: util.getAttrsOfCls(inheritor)})

ATTR_INFOS_TO_SIMPLIFY = (AdministrativeInformation, LangStringSet)

DICT_TYPES = (dict, LangStringSet)
TYPES_NOT_TO_POPULATE = (type, ABCMeta)
TYPES_WITH_INSTANCES_NOT_TO_POPULATE = (
    AbstractObjectStore, str, int, float, bool, Enum, Path, aas_editor.additional.classes.DictItem, datatypes.Decimal, type,
    datetime.date)  # '+ TYPES_IN_ONE_ROW
COMPLEX_ITERABLE_TYPES = (Namespace, import_util_classes.PreObjectImport)

TYPE_SHORTS_DICT = {
    AssetAdministrationShell: "aas",
    ConceptDescription: "cd",
    Submodel: "sm",
    Property: "prop",
    Entity: "ent",
    Capability: "cap",
    BasicEventElement: "evnt",
    Operation: "opr",
    RelationshipElement: "rel",
    AnnotatedRelationshipElement: "arel",
    SubmodelElementCollection: "smc",
    SubmodelElementList: "sml",
    Range: "rng",
    Blob: "blob",
    File: "file",
    ReferenceElement: "ref",
    DataElement: "data",
}

# produce char icon objects from str dict
TYPE_ICON_DICT = {typ: getCharsIcon(shortname) for typ, shortname in TYPE_SHORTS_DICT.items()}
