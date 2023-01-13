#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/

from basyx.aas.model import Key, KeyTypes, AssetKind, File, Blob, SubmodelElement, \
    Property, Qualifier, Referable, AssetAdministrationShell
from basyx.aas.model.datatypes import String

from aas_editor.additional.classes import DictItem

CATEGORIES = ["CONSTANT", "PARAMETER", "VARIABLE"]

LANGUAGES = [
    "DE",
    "EN",
    "FR",
    "IT",
    "JA",
]

MIME_TYPES = [
    "application/graphql",
    "application/javascript",
    "application/json",
    "application/ld+json",
    "application/msw",
    "application/pdf",
    "application/sql",
    "application/vnd.api+json",
    "application/vnd.ms-excel",
    "application/vnd.ms-powerpoint",
    "application/vnd.oasis.opendocument.text",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/x-www-form-urlencoded",
    "application/xml",
    "application/zip",
    "application/zstd",
    "audio/mpeg",
    "audio/ogg",
    "image/gif",
    "image/jpeg",
    "image/png",
    "multipart/form-data",
    "text/css",
    "text/csv",
    "text/html",
    "text/php",
    "text/plain",
    "text/xml",
]

DEFAULT_INHERITOR = {
    SubmodelElement: Property,
}

DEFAULTS = {
    Key: {
        "type_": KeyTypes.PROPERTY,
        "value": "https://www.company.com/",
    },
    Property: {
        "value_type": String,
    },
}

DEFAULT_COMPLETIONS = {
    Key: {
        "value": []
    },
    File: {
        "mime_type": MIME_TYPES
    },
    Blob: {
        "mime_type": MIME_TYPES
    },
    DictItem: {
        "key": LANGUAGES
    },
    Property: {
        "category": CATEGORIES
    }
}
