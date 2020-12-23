from aas.model import Key, KeyType, Asset, AssetKind, Identifier, IdentifierType, File, Blob

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

DEFAULTS = {
    Key: {
        "id_type": KeyType.IRI,
        "value": "https://www.company.com/"
    },
    Identifier: {
        "id_": "https://www.company.com/",
        "id_type": IdentifierType.IRI,
    },
    Asset: {
        "kind": AssetKind.INSTANCE,
    }
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
