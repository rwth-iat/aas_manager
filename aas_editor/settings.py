from aas.model import AdministrativeInformation, Identifier

ATTR_COLUMN_WIDTH = 200

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

PREFERED_THEME = "dark"

DARK_THEME_PATH = "themes/dark.qss"
LIGHT_THEME_PATH = "themes/light.qss"

THEMES = {
    "dark": DARK_THEME_PATH,
    "light": LIGHT_THEME_PATH,
}

PACKAGE_ATTRS = ("shells", "assets", "submodels", "concept_descriptions")
ATTRS_NOT_IN_DETAILED_INFO = ("namespace_element_sets", "parent") + PACKAGE_ATTRS
ATTRS_IN_PACKAGE_TREEVIEW = PACKAGE_ATTRS
ATTR_INFOS_TO_SIMPLIFY = (AdministrativeInformation, Identifier,)