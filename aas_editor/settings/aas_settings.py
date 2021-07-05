import datetime
from abc import ABCMeta
from enum import Enum
from pathlib import Path

import dateutil
from aas.model import AssetAdministrationShell, Asset, ConceptDescription, Submodel, Property, \
    Entity, Capability, Event, Operation, RelationshipElement, AnnotatedRelationshipElement, \
    SubmodelElementCollectionUnordered, SubmodelElementCollectionOrdered, Range, Blob, File, \
    ReferenceElement, DataElement, AdministrativeInformation, Identifier, AbstractObjectStore, \
    Namespace, SubmodelElementCollection, SubmodelElement, AASReference, ConceptDictionary

import aas_editor.package
from aas_editor.settings import getCharsIcon, HIDDEN_ATTRS, CHANGED_PARENT_OBJ, ADD_ACT_AAS_TXT, \
    ADD_TYPE, PACKVIEW_ATTRS_INFO
from aas_editor.utils import util_classes

AAS_FILES_FILTER = "AAS files (*.aasx *.xml *.json)"
AASX_FILES_FILTER = "AASX files (*.aasx)"
XML_FILES_FILTER = "XML files (*.xml)"
JSON_FILES_FILTER = "JSON files (*.json)"
ALL_FILES_FILTER = "All files (*.*)"

FILE_TYPE_FILTERS = {
    "AASX": AASX_FILES_FILTER,
    "XML": XML_FILES_FILTER,
    "JSON": JSON_FILES_FILTER
}
FILTER_AAS_FILES = f"{AAS_FILES_FILTER};;{AASX_FILES_FILTER};;{XML_FILES_FILTER};;{JSON_FILES_FILTER};;{ALL_FILES_FILTER}"

EMPTY_VALUES = (None, tuple(), set(), list(), dict())

LINK_TYPES = (AASReference,)
MEDIA_TYPES = (File, Blob, aas_editor.package.StoredFile)

# AnyXSDType = Base64Binary, HexBinary

from aas import model

TYPE_NAMES_DICT = {
    model.datatypes.String: "String",
    model.datatypes.Boolean: "Boolean",
    model.datatypes.Double: "Double",
    model.datatypes.Decimal: "Decimal",
    model.datatypes.Int: "Integer",
    int: "Integer",
    model.datatypes.Duration: "Duration",
    model.datatypes.DateTime: "DateTime",
    model.datatypes.Date: "Date",
    model.datatypes.Time: "Time",
    model.datatypes.GYearMonth: "GYearMonth",
    model.datatypes.GYear: "GYear",
    model.datatypes.GMonthDay: "GMonthDay",
    model.datatypes.GMonth: "GMonth",
    model.datatypes.GDay: "GDay",
    model.datatypes.Base64Binary: "Base64Binary",
    model.datatypes.HexBinary: "HexBinary",
    model.datatypes.Float: "Float",
    model.datatypes.Long: "Long",
    model.datatypes.Short: "Short",
    model.datatypes.Byte: "Byte",
    model.datatypes.NonPositiveInteger: "NonPositiveInteger",
    model.datatypes.NegativeInteger: "NegativeInteger",
    model.datatypes.NonNegativeInteger: "NonNegativeInteger",
    model.datatypes.PositiveInteger: "PositiveInteger",
    model.datatypes.UnsignedLong: "UnsignedLong",
    model.datatypes.UnsignedInt: "UnsignedInt",
    model.datatypes.UnsignedShort: "UnsignedShort",
    model.datatypes.UnsignedByte: "UnsignedByte",
    model.datatypes.AnyURI: "AnyURI",
    model.datatypes.NormalizedString: "NormalizedString",
    model.base.Identifier:
        {"class": "Identifier",
         "attributes":
             {"idType": "id_type",
              "id": "id_"
              }
         },
    model.base.AdministrativeInformation:
        {"class": "AdministrativeInformation",
         "attributes":
             {"version": "version",
              "revision": "revision"
              }
         },
    model.base.Qualifier:
        {"class": "Qualifier",
         "attributes":
             {"semanticId": "semantic_id",
              "type": "type_",
              "valueType": "value_type",
              "value": "value",
              "valueId": "value_id"
              }
         },
    model.submodel.Submodel:
        {"class": "Submodel",
         "attributes":
             {"idShort": "id_short",
              "displayName": "display_name",
              "category": "category",
              "description": "description",
              "administration": "administration",
              "identification": "identification",
              "kind": "kind",
              "semanticId": "semantic_id",
              "qualifier": "qualifier",
              "extension": "extension",
              "submodelElement": "submodel_element"
              }
         },
    model.submodel.SubmodelElement:
        {"class": "SubmodelElement",
         "attributes":
             {"idShort": "id_short",
              "displayName": "display_name",
              "category": "category",
              "description": "description",
              "kind": "kind",
              "semanticId": "semantic_id",
              "qualifier": "qualifier",
              "extension": "extension"
              }
         },
    model.submodel.AnnotatedRelationshipElement:
        {"class": "AnnotatedRelationshipElement",
         "attributes":
             {"idShort": "id_short",
              "displayName": "display_name",
              "category": "category",
              "description": "description",
              "kind": "kind",
              "semanticId": "semantic_id",
              "qualifier": "qualifier",
              "extension": "extension",
              "first": "first",
              "second": "second",
              "annotation": "annotation"
              }
         },
    model.submodel.BasicEvent:
        {"class": "BasicEvent",
         "attributes":
             {"idShort": "id_short",
              "displayName": "display_name",
              "category": "category",
              "description": "description",
              "kind": "kind",
              "semanticId": "semantic_id",
              "qualifier": "qualifier",
              "extension": "extension",
              "observed": "observed"
              }
         },
    model.submodel.Capability:
        {"class": "Capability",
         "attributes":
             {"idShort": "id_short",
              "displayName": "display_name",
              "category": "category",
              "description": "description",
              "kind": "kind",
              "semanticId": "semantic_id",
              "qualifier": "qualifier",
              "extension": "extension",
              }
         },
    model.submodel.Blob:
        {"class": "Blob",
         "attributes":
             {"idShort": "id_short",
              "displayName": "display_name",
              "category": "category",
              "description": "description",
              "kind": "kind",
              "semanticId": "semantic_id",
              "qualifier": "qualifier",
              "extension": "extension",
              "value": "value",
              "mimeType": "mime_type"
              }
         },
    model.submodel.Entity:
        {"class": "Entity",
         "attributes":
             {"idShort": "id_short",
              "displayName": "display_name",
              "category": "category",
              "description": "description",
              "kind": "kind",
              "semanticId": "semantic_id",
              "qualifier": "qualifier",
              "extension": "extension",
              "statement": "statement",
              "entityType": "entity_type",
              "globalAssetId": "global_asset_id",
              "specificAssetId": "specific_asset_id"
              }
         },

    model.submodel.File:
        {"class": "File",
         "attributes":
             {"idShort": "id_short",
              "displayName": "display_name",
              "category": "category",
              "description": "description",
              "kind": "kind",
              "semanticId": "semantic_id",
              "qualifier": "qualifier",
              "extension": "extension",
              "value": "value",
              "mimeType": "mime_type"
              }
         },
    model.submodel.MultiLanguageProperty:
        {"class": "MultiLanguageProperty",
         "attributes":
             {"idShort": "id_short",
              "displayName": "display_name",
              "category": "category",
              "description": "description",
              "kind": "kind",
              "semanticId": "semantic_id",
              "qualifier": "qualifier",
              "extension": "extension",
              "value": "value",
              "valueId": "value_id"
              }
         },
    model.submodel.Operation:
        {"class": "Operation",
         "attributes":
             {"idShort": "id_short",
              "displayName": "display_name",
              "category": "category",
              "description": "description",
              "kind": "kind",
              "semanticId": "semantic_id",
              "qualifier": "qualifier",
              "extension": "extension",
              "inputVariable": "input_variable",
              "outputVariable": "output_variable",
              "inoutputVariable": "in_output_variable"
              }
         },
    model.submodel.OperationVariable:
        {"class": "OperationVariable",
         "attributes":
             {"idShort": "id_short",
              "displayName": "display_name",
              "category": "category",
              "description": "description",
              "kind": "kind",
              "semanticId": "semantic_id",
              "qualifier": "qualifier",
              "extension": "extension",
              "value": "value"
              }
         },
    model.submodel.Property:
        {"class": "Property",
         "attributes":
             {"idShort": "id_short",
              "displayName": "display_name",
              "category": "category",
              "description": "description",
              "kind": "kind",
              "semanticId": "semantic_id",
              "qualifier": "qualifier",
              "extension": "extension",
              "valueType": "value_type",
              "value": "value",
              "valueId": "value_id"
              }
         },
    model.submodel.Range:
        {"class": "Range",
         "attributes":
             {"idShort": "id_short",
              "displayName": "display_name",
              "category": "category",
              "description": "description",
              "kind": "kind",
              "semanticId": "semantic_id",
              "qualifier": "qualifier",
              "extension": "extension",
              "valueType": "value_type",
              "min": "min",
              "max": "max",
              }
         },
    model.submodel.ReferenceElement:
        {"class": "ReferenceElement",
         "attributes":
             {"idShort": "id_short",
              "displayName": "display_name",
              "category": "category",
              "description": "description",
              "kind": "kind",
              "semanticId": "semantic_id",
              "qualifier": "qualifier",
              "extension": "extension",
              "value": "value"
              }
         },
    model.submodel.RelationshipElement:
        {"class": "RelationshipElement",
         "attributes":
             {"idShort": "id_short",
              "displayName": "display_name",
              "category": "category",
              "description": "description",
              "kind": "kind",
              "semanticId": "semantic_id",
              "qualifier": "qualifier",
              "extension": "extension",
              "first": "first",
              "second": "second"
              }
         },
    model.submodel.SubmodelElementCollection:
        {"class": "SubmodelElementCollection",
         "attributes":
             {"idShort": "id_short",
              "displayName": "display_name",
              "category": "category",
              "description": "description",
              "kind": "kind",
              "semanticId": "semantic_id",
              "qualifier": "qualifier",
              "extension": "extension",
              "value": "value",
              "ordered": "ordered",
              "allowDuplicates": "allow_duplicates"
              }
         },
    model.base.Reference:
        {"class": "Reference",
         "attributes":
             {"key": "key"
              }
         },
    model.base.Key:
        {"class": "Key",
         "attributes":
             {"type": "type_",
              "value": "value",
              "idType": "id_type"
              }
         }
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
    "identification",
)
PREFERED_LANGS_ORDER = ("en-us", "en", "de")

CLASSES_INFO = {
    object: {
        HIDDEN_ATTRS: (
            "namespace_element_sets", "parent", "security", "source")
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
            "assets": {
                ADD_ACT_AAS_TXT: "Add asset",
                ADD_TYPE: Asset,
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
        }
    },
    AssetAdministrationShell: {
        CHANGED_PARENT_OBJ: "concept_dictionary",
        ADD_ACT_AAS_TXT: "Add concept dictionary",
        ADD_TYPE: ConceptDictionary,
    },
    Submodel: {
        HIDDEN_ATTRS: ("submodel_element",),
        CHANGED_PARENT_OBJ: "submodel_element",
        ADD_ACT_AAS_TXT: "Add submodel element",
        ADD_TYPE: SubmodelElement,
    },
    AnnotatedRelationshipElement: {
        HIDDEN_ATTRS: ("annotation",),
        CHANGED_PARENT_OBJ: "annotation",
        ADD_ACT_AAS_TXT: "Add annotation",
        ADD_TYPE: DataElement,
    },
    SubmodelElementCollection: {
        HIDDEN_ATTRS: ("value",),
        CHANGED_PARENT_OBJ: "value",
        ADD_ACT_AAS_TXT: "Add collection submodel element",
        ADD_TYPE: SubmodelElement,
    },
    Entity: {
        HIDDEN_ATTRS: ("statement",),
        CHANGED_PARENT_OBJ: "statement",
        ADD_ACT_AAS_TXT: "Add statement",
        ADD_TYPE: SubmodelElement,
    },
}


ATTR_INFOS_TO_SIMPLIFY = (AdministrativeInformation, Identifier,)

TYPES_NOT_TO_POPULATE = (type, ABCMeta)
TYPES_WITH_INSTANCES_NOT_TO_POPULATE = (
    AbstractObjectStore, str, int, float, bool, Enum, Path, util_classes.DictItem)  # '+ TYPES_IN_ONE_ROW
COMPLEX_ITERABLE_TYPES = (Namespace,)
DEFAULT_ATTRS_TO_HIDE = {"parent": None}

TYPE_SHORTS_DICT = {
    AssetAdministrationShell: "aas",
    Asset: "ast",
    ConceptDescription: "cd",
    Submodel: "sm",
    Property: "prop",
    Entity: "ent",
    Capability: "cap",
    Event: "evnt",
    Operation: "opr",
    RelationshipElement: "rel",
    AnnotatedRelationshipElement: "arel",
    SubmodelElementCollectionUnordered: "smc",
    SubmodelElementCollectionOrdered: "smc",
    Range: "rng",
    Blob: "blob",
    File: "file",
    ReferenceElement: "ref",
    DataElement: "data",
}

# produce char icon objects from str dict
TYPE_ICON_DICT = {typ: getCharsIcon(TYPE_SHORTS_DICT[typ]) for typ in TYPE_SHORTS_DICT}
