from basyx.aas.model import AssetAdministrationShell, Submodel, ConceptDescription

from aas_editor.package import Package, StoredFile
from aas_editor.settings.aas_settings import (
    CLASSES_INFO, MEDIA_TYPES_INFOS,
    HIDDEN_ATTRS, ADD_ACT_AAS_TXT, ADD_TYPE, PACKVIEW_ATTRS_INFO, IS_EDITABLE_IN_GUI,
    CONTENT_TYPE_ATTR, CONTENT_VALUE_ATTR,
    SHELLS, SUBMODELS, CONCEPT_DESCRIPTIONS, FILESTORE,
)

MEDIA_TYPES_INFOS[StoredFile] = {
    CONTENT_TYPE_ATTR: "mime_type",
    CONTENT_VALUE_ATTR: "value",
}

CLASSES_INFO[Package] = {
    HIDDEN_ATTRS: ("ATTRS_INFO", "shells", "assets", "submodels", "concept_descriptions", "others", "fileStore"),
    ADD_ACT_AAS_TXT: "Add package",
    ADD_TYPE: Package,
    PACKVIEW_ATTRS_INFO: {
        SHELLS: {ADD_ACT_AAS_TXT: "Add shell", ADD_TYPE: AssetAdministrationShell},
        SUBMODELS: {ADD_ACT_AAS_TXT: "Add submodel", ADD_TYPE: Submodel},
        CONCEPT_DESCRIPTIONS: {ADD_ACT_AAS_TXT: "Add concept description", ADD_TYPE: ConceptDescription},
        FILESTORE: {ADD_ACT_AAS_TXT: "Add file", ADD_TYPE: StoredFile},
    },
    IS_EDITABLE_IN_GUI: False,
}
