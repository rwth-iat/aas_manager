from aas.model import Key, KeyType, Asset, AssetKind, Identifier, IdentifierType

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