from enum import Enum
from pathlib import Path

from aas.model import AssetAdministrationShell, Asset, ConceptDescription, Submodel, Property, \
    Entity, Capability, Event, Operation, RelationshipElement, AnnotatedRelationshipElement, \
    SubmodelElementCollectionUnordered, SubmodelElementCollectionOrdered, Range, Blob, File, \
    ReferenceElement, DataElement, AdministrativeInformation, Identifier, AbstractObjectStore, \
    Namespace, SubmodelElementCollection

from aas_editor import util_classes
from aas_editor.settings.app_settings import getCharsIcon


TYPE_ICON_DICT = {
    AssetAdministrationShell: getCharsIcon("shl"),  # qta.icon("mdi.wallet") #  mdi.tab mdi.shredder folder-outline wallet
    Asset: getCharsIcon("ast"),  # qta.icon("mdi.mini-sd") # mdi.toy-brick
    ConceptDescription: getCharsIcon("cnc"),  # qta.icon("mdi.text-box")
    Submodel: getCharsIcon("sub"),

    Property: getCharsIcon("prp"),
    Entity: getCharsIcon("ent"),
    Capability: getCharsIcon("cap"),
    Event: getCharsIcon("evnt"),  # qta.icon("mdi.timeline-clock")  # mdi.timer mdi.bell
    Operation: getCharsIcon("opr"),  # qta.icon("mdi.cog")
    RelationshipElement: getCharsIcon("rel"),
    AnnotatedRelationshipElement: getCharsIcon("rel"), # qta.icon("mdi.arrow-left-right")  # mdi.relation-one-to-one
    SubmodelElementCollectionUnordered: getCharsIcon("col"),
    SubmodelElementCollectionOrdered: getCharsIcon("col"),  # qta.icon("mdi.package")

    Range: getCharsIcon("rng"),
    Blob: getCharsIcon("blb"),
    File: getCharsIcon("file"),
    ReferenceElement: getCharsIcon("ref"),
    DataElement: getCharsIcon("data"),
}
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
PREFERED_LANGS_ORDER = ("en-us", "en", "de")

AAS_REF_PARENT_OBJECTS = {
    Submodel: "submodel_element",
    AnnotatedRelationshipElement: "annotation",
    SubmodelElementCollection: "value",
    Entity: "statement"
}

CLS_ATTRS_NOT_IN_DETAILED_INFO = {
    object: ("namespace_element_sets", "parent", "security"),#TODO delete when implemented in aas
    util_classes.Package: ("ATTRS", *util_classes.Package.ATTRS),
    **AAS_REF_PARENT_OBJECTS
}


ATTR_INFOS_TO_SIMPLIFY = (AdministrativeInformation, Identifier,)
TYPES_NOT_TO_POPULATE = (
    AbstractObjectStore, str, int, float, bool, Enum, Path, util_classes.DictItem)  # '+ TYPES_IN_ONE_ROW
COMPLEX_ITERABLE_TYPES = (Namespace,)
DEFAULT_ATTRS_TO_HIDE = {"parent": None}
