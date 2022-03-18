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

from basyx.aas.model import Key, KeyType, Asset, AssetKind, Identifier, IdentifierType, File, Blob, SubmodelElement, Property, \
    Constraint, Qualifier, AASReference, Identifiable
from basyx.aas.model.datatypes import String

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
    Constraint: Qualifier,
}

DEFAULTS = {
    Key: {
        "id_type": KeyType.IRI,
        "value": "https://www.company.com/",
        "local": True
    },
    Identifier: {
        "id_": "https://www.company.com/",
        "id_type": IdentifierType.IRI,
    },
    Asset: {
        "kind": AssetKind.INSTANCE,
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
}
