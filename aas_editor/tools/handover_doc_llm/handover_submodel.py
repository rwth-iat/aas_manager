from typing import *
import inspect
from basyx.aas.model import *
from basyx.aas.model.datatypes import *


class HandoverDocumentation(Submodel):
    class Documents(SubmodelElementList):
        class Documents_item(SubmodelElementCollection):
            class DocumentIds(SubmodelElementList):
                class Documentids_item(SubmodelElementCollection):
                    class DocumentDomainId(Property):
                        def __init__(
                            self,
                            value: str,
                            id_short: Optional[str] = "DocumentDomainId",
                            value_type: DataTypeDefXsd = str,
                            value_id: Optional[Reference] = None,
                            display_name: Optional[
                                MultiLanguageNameType
                            ] = MultiLanguageNameType(
                                dict_={
                                    "en": "document domain identificator",
                                    "de": "Document Domain Identifikator",
                                }
                            ),
                            category: Optional[str] = "PARAMETER",
                            description: Optional[MultiLanguageTextType] = None,
                            semantic_id: Optional[Reference] = ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="0173-1#02-ABH994#003",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                            qualifier: Iterable[Qualifier] = None,
                            extension: Iterable[Extension] = (),
                            supplemental_semantic_id: Iterable[Reference] = (
                                ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="https://api.eclass-cdp.com/0173-1-02-ABH994-003",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                            ),
                            embedded_data_specifications: Iterable[
                                EmbeddedDataSpecification
                            ] = None,
                        ):
                            if qualifier is None:
                                qualifier = (
                                    Qualifier(
                                        type_="SMT/Cardinality",
                                        value_type=str,
                                        value="One",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                    Qualifier(
                                        type_="ExampleValue",
                                        value_type=str,
                                        value="https://domain.com/...",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/ExampleValue/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                )

                            if embedded_data_specifications is None:
                                embedded_data_specifications = []

                            super().__init__(
                                value=value,
                                id_short=id_short,
                                value_type=value_type,
                                value_id=value_id,
                                display_name=display_name,
                                category=category,
                                description=description,
                                semantic_id=semantic_id,
                                qualifier=qualifier,
                                extension=extension,
                                supplemental_semantic_id=supplemental_semantic_id,
                                embedded_data_specifications=embedded_data_specifications,
                            )

                    class DocumentIdentifier(Property):
                        def __init__(
                            self,
                            value: str,
                            id_short: Optional[str] = "DocumentIdentifier",
                            value_type: DataTypeDefXsd = str,
                            value_id: Optional[Reference] = None,
                            display_name: Optional[
                                MultiLanguageNameType
                            ] = MultiLanguageNameType(
                                dict_={
                                    "en": "Document Identifyer",
                                    "de": "Dokumentennummer",
                                }
                            ),
                            category: Optional[str] = "PARAMETER",
                            description: Optional[MultiLanguageTextType] = None,
                            semantic_id: Optional[Reference] = ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="0173-1#02-AAO099#004",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                            qualifier: Iterable[Qualifier] = None,
                            extension: Iterable[Extension] = (),
                            supplemental_semantic_id: Iterable[Reference] = (
                                ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="https://api.eclass-cdp.com/0173-1-02-AAO099-004",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                            ),
                            embedded_data_specifications: Iterable[
                                EmbeddedDataSpecification
                            ] = None,
                        ):
                            if qualifier is None:
                                qualifier = (
                                    Qualifier(
                                        type_="SMT/Cardinality",
                                        value_type=str,
                                        value="One",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                    Qualifier(
                                        type_="ExampleValue",
                                        value_type=str,
                                        value="XF90-884",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/ExampleValue/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                )

                            if embedded_data_specifications is None:
                                embedded_data_specifications = []

                            super().__init__(
                                value=value,
                                id_short=id_short,
                                value_type=value_type,
                                value_id=value_id,
                                display_name=display_name,
                                category=category,
                                description=description,
                                semantic_id=semantic_id,
                                qualifier=qualifier,
                                extension=extension,
                                supplemental_semantic_id=supplemental_semantic_id,
                                embedded_data_specifications=embedded_data_specifications,
                            )

                    class DocumentIsPrimary(Property):
                        def __init__(
                            self,
                            value: bool,
                            id_short: Optional[str] = "DocumentIsPrimary",
                            value_type: DataTypeDefXsd = bool,
                            value_id: Optional[Reference] = None,
                            display_name: Optional[
                                MultiLanguageNameType
                            ] = MultiLanguageNameType(
                                dict_={
                                    "en": "Document is primary",
                                    "de": "Dokument ist primär",
                                }
                            ),
                            category: Optional[str] = "PARAMETER",
                            description: Optional[MultiLanguageTextType] = None,
                            semantic_id: Optional[Reference] = ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="0173-1#02-ABH995#003",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                            qualifier: Iterable[Qualifier] = None,
                            extension: Iterable[Extension] = (),
                            supplemental_semantic_id: Iterable[Reference] = (
                                ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="https://api.eclass-cdp.com/0173-1-02-ABH995-003",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                            ),
                            embedded_data_specifications: Iterable[
                                EmbeddedDataSpecification
                            ] = None,
                        ):
                            if qualifier is None:
                                qualifier = (
                                    Qualifier(
                                        type_="SMT/Cardinality",
                                        value_type=str,
                                        value="ZeroToOne",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                    Qualifier(
                                        type_="ExampleValue",
                                        value_type=str,
                                        value="true",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/ExampleValue/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                )

                            if embedded_data_specifications is None:
                                embedded_data_specifications = []

                            super().__init__(
                                value=value,
                                id_short=id_short,
                                value_type=value_type,
                                value_id=value_id,
                                display_name=display_name,
                                category=category,
                                description=description,
                                semantic_id=semantic_id,
                                qualifier=qualifier,
                                extension=extension,
                                supplemental_semantic_id=supplemental_semantic_id,
                                embedded_data_specifications=embedded_data_specifications,
                            )

                    def __init__(
                        self,
                        documentDomainId: Union[str, DocumentDomainId],
                        documentIdentifier: Union[str, DocumentIdentifier],
                        documentIsPrimary: Optional[
                            Union[bool, DocumentIsPrimary]
                        ] = None,
                        id_short: Optional[str] = None,
                        display_name: Optional[
                            MultiLanguageNameType
                        ] = MultiLanguageNameType(
                            dict_={
                                "en": "Document identificator",
                                "de": "Dokumentidentifikator",
                            }
                        ),
                        category: Optional[str] = None,
                        description: Optional[
                            MultiLanguageTextType
                        ] = MultiLanguageTextType(
                            dict_={
                                "en": "This SubmodelElementCollection holds the information for a VDI 2770 Document entity"
                            }
                        ),
                        semantic_id: Optional[Reference] = ExternalReference(
                            key=(
                                Key(
                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                    value="0173-1#02-ABI501#003/0173-1#01-AHF580#003",
                                ),
                            ),
                            referred_semantic_id=None,
                        ),
                        qualifier: Iterable[Qualifier] = None,
                        extension: Iterable[Extension] = (),
                        supplemental_semantic_id: Iterable[Reference] = (
                            ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="0173-1#02-ABI501#003~0/0173-1#01-AHF580#003",
                                    ),
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="https://api.eclass-cdp.com/0173-1-02-ABI501-003/0173-1-01-AHF580-003",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                        ),
                        embedded_data_specifications: Iterable[
                            EmbeddedDataSpecification
                        ] = None,
                    ):
                        if qualifier is None:
                            qualifier = (
                                Qualifier(
                                    type_="SMT/Cardinality",
                                    value_type=str,
                                    value="OneToMany",
                                    value_id=None,
                                    kind=QualifierKind.CONCEPT_QUALIFIER,
                                    semantic_id=ExternalReference(
                                        key=(
                                            Key(
                                                type_=KeyTypes.GLOBAL_REFERENCE,
                                                value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                            ),
                                        ),
                                        referred_semantic_id=None,
                                    ),
                                    supplemental_semantic_id=(),
                                ),
                            )

                        if embedded_data_specifications is None:
                            embedded_data_specifications = []

                        # Build a submodel element if a raw value was passed in the argument
                        if documentDomainId and not isinstance(
                            documentDomainId, SubmodelElement
                        ):
                            documentDomainId = self.DocumentDomainId(documentDomainId)

                        # Build a submodel element if a raw value was passed in the argument
                        if documentIdentifier and not isinstance(
                            documentIdentifier, SubmodelElement
                        ):
                            documentIdentifier = self.DocumentIdentifier(
                                documentIdentifier
                            )

                        # Build a submodel element if a raw value was passed in the argument
                        if documentIsPrimary and not isinstance(
                            documentIsPrimary, SubmodelElement
                        ):
                            documentIsPrimary = self.DocumentIsPrimary(
                                documentIsPrimary
                            )

                        # Add all passed/initialized submodel elements to a single list
                        embedded_submodel_elements = []
                        for se_arg in [
                            documentDomainId,
                            documentIdentifier,
                            documentIsPrimary,
                        ]:
                            if se_arg is None:
                                continue
                            elif isinstance(se_arg, SubmodelElement):
                                embedded_submodel_elements.append(se_arg)
                            elif isinstance(se_arg, Iterable):
                                for n, element in enumerate(se_arg):
                                    element.id_short = f"{element.id_short}{n}"
                                    embedded_submodel_elements.append(element)
                            else:
                                raise TypeError(
                                    f"Unknown type of value in submodel_element_args: {type(se_arg)}"
                                )

                        super().__init__(
                            value=embedded_submodel_elements,
                            id_short=id_short,
                            display_name=display_name,
                            category=category,
                            description=description,
                            semantic_id=semantic_id,
                            qualifier=qualifier,
                            extension=extension,
                            supplemental_semantic_id=supplemental_semantic_id,
                            embedded_data_specifications=embedded_data_specifications,
                        )

                def __init__(
                    self,
                    documentids_items: Iterable[Documentids_item],
                    id_short: Optional[str] = "DocumentIds",
                    type_value_list_element: SubmodelElement = SubmodelElementCollection,
                    semantic_id_list_element: Optional[Reference] = ExternalReference(
                        key=(
                            Key(
                                type_=KeyTypes.GLOBAL_REFERENCE,
                                value="0173-1#02-ABI501#003/0173-1#01-AHF580#003",
                            ),
                        ),
                        referred_semantic_id=None,
                    ),
                    value_type_list_element: Optional[DataTypeDefXsd] = None,
                    order_relevant: bool = True,
                    display_name: Optional[
                        MultiLanguageNameType
                    ] = MultiLanguageNameType(
                        dict_={
                            "en": "Document identifyers",
                            "de": "Dokumentidentifikatoren",
                        }
                    ),
                    category: Optional[str] = None,
                    description: Optional[MultiLanguageTextType] = None,
                    semantic_id: Optional[Reference] = ExternalReference(
                        key=(
                            Key(
                                type_=KeyTypes.GLOBAL_REFERENCE,
                                value="0173-1#02-ABI501#003",
                            ),
                        ),
                        referred_semantic_id=None,
                    ),
                    qualifier: Iterable[Qualifier] = None,
                    extension: Iterable[Extension] = (),
                    supplemental_semantic_id: Iterable[Reference] = (
                        ExternalReference(
                            key=(
                                Key(
                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                    value="https://api.eclass-cdp.com/0173-1-02-ABI501-003",
                                ),
                            ),
                            referred_semantic_id=None,
                        ),
                    ),
                    embedded_data_specifications: Iterable[
                        EmbeddedDataSpecification
                    ] = None,
                ):
                    if qualifier is None:
                        qualifier = (
                            Qualifier(
                                type_="SMT/Cardinality",
                                value_type=str,
                                value="One",
                                value_id=None,
                                kind=QualifierKind.CONCEPT_QUALIFIER,
                                semantic_id=ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                                supplemental_semantic_id=(),
                            ),
                        )

                    if embedded_data_specifications is None:
                        embedded_data_specifications = []

                    # Add all passed/initialized submodel elements to a single list
                    embedded_submodel_elements = []
                    for se_arg in [documentids_items]:
                        if se_arg is None:
                            continue
                        elif isinstance(se_arg, SubmodelElement):
                            embedded_submodel_elements.append(se_arg)
                        elif isinstance(se_arg, Iterable):
                            for n, element in enumerate(se_arg):
                                element.id_short = f"{element.id_short}{n}"
                                embedded_submodel_elements.append(element)
                        else:
                            raise TypeError(
                                f"Unknown type of value in submodel_element_args: {type(se_arg)}"
                            )

                    super().__init__(
                        value=embedded_submodel_elements,
                        id_short=id_short,
                        type_value_list_element=type_value_list_element,
                        semantic_id_list_element=semantic_id_list_element,
                        value_type_list_element=value_type_list_element,
                        order_relevant=order_relevant,
                        display_name=display_name,
                        category=category,
                        description=description,
                        semantic_id=semantic_id,
                        qualifier=qualifier,
                        extension=extension,
                        supplemental_semantic_id=supplemental_semantic_id,
                        embedded_data_specifications=embedded_data_specifications,
                    )

                def _check_constraints(self, new, existing) -> None:
                    # Since the id_short contains randomness, unset it temporarily for pretty and predictable error messages.
                    # This also prevents the random id_short from remaining set in case a constraint violation is encountered.
                    saved_id_short = new.id_short
                    new.id_short = None

                    # We relax constraint AASd-108here: It is allowed to add subclasses of the specified in type_value_list_element
                    if not isinstance(new, self.type_value_list_element):
                        raise base.AASConstraintViolation(
                            108,
                            "All first level elements must be of the type specified in "
                            f"type_value_list_element={self.type_value_list_element.__name__}, "
                            f"got {new!r}",
                        )

                    if (
                        self.semantic_id_list_element is not None
                        and new.semantic_id is not None
                        and new.semantic_id != self.semantic_id_list_element
                    ):
                        # Constraint AASd-115 specifies that if the semantic_id of an item is not specified
                        # but semantic_id_list_element is, the semantic_id of the new is assumed to be identical.
                        # Not really a constraint...
                        # TODO: maybe set the semantic_id of new to semantic_id_list_element if it is None
                        raise base.AASConstraintViolation(
                            107,
                            f"If semantic_id_list_element={self.semantic_id_list_element!r} "
                            "is specified all first level children must have the same "
                            f"semantic_id, got {new!r} with semantic_id={new.semantic_id!r}",
                        )

                    # If we got here we know that `new` is an instance of type_value_list_element and that type_value_list_element
                    # is either Property or Range. Thus, `new` must have the value_type property.
                    # Furthermore, value_type_list_element cannot be None, as this is already checked in __init__().
                    if (
                        isinstance(self.type_value_list_element, Property)
                        or isinstance(self.type_value_list_element, Range)
                        and not isinstance(new.value_type, self.value_type_list_element)
                    ):  # type: ignore
                        raise base.AASConstraintViolation(
                            109,
                            "All first level elements must have the value_type "  # type: ignore
                            "specified by value_type_list_element="
                            f"{self.value_type_list_element.__name__}, got "  # type: ignore
                            f"{new!r} with value_type={new.value_type.__name__}",
                        )  # type: ignore

                    # If semantic_id_list_element is not None that would already enforce the semantic_id for all first level
                    # elements. Thus, we only need to perform this check if semantic_id_list_element is None.
                    if (
                        new.semantic_id is not None
                        and self.semantic_id_list_element is None
                    ):
                        for item in existing:
                            if (
                                item.semantic_id is not None
                                and new.semantic_id != item.semantic_id
                            ):
                                raise base.AASConstraintViolation(
                                    114,
                                    f"Element to be added {new!r} has semantic_id "
                                    f"{new.semantic_id!r}, while already contained element "
                                    f"{item!r} has semantic_id {item.semantic_id!r}, which "
                                    "aren't equal.",
                                )

                    # Re-assign id_short
                    new.id_short = saved_id_short

            class DocumentClassifications(SubmodelElementList):
                class Documentclassifications_item(SubmodelElementCollection):
                    class ClassId(Property):
                        def __init__(
                            self,
                            value: str,
                            id_short: Optional[str] = "ClassId",
                            value_type: DataTypeDefXsd = str,
                            value_id: Optional[Reference] = None,
                            display_name: Optional[
                                MultiLanguageNameType
                            ] = MultiLanguageNameType(
                                dict_={
                                    "en": "Class identificator",
                                    "de": "Klassenidentifikator",
                                }
                            ),
                            category: Optional[str] = "PARAMETER",
                            description: Optional[MultiLanguageTextType] = None,
                            semantic_id: Optional[Reference] = ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="0173-1#02-ABH996#003",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                            qualifier: Iterable[Qualifier] = None,
                            extension: Iterable[Extension] = (),
                            supplemental_semantic_id: Iterable[Reference] = (
                                ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="https://api.eclass-cdp.com/0173-1-02-ABH996-003",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                            ),
                            embedded_data_specifications: Iterable[
                                EmbeddedDataSpecification
                            ] = None,
                        ):
                            if qualifier is None:
                                qualifier = (
                                    Qualifier(
                                        type_="SMT/Cardinality",
                                        value_type=str,
                                        value="One",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                    Qualifier(
                                        type_="ExampleValue",
                                        value_type=str,
                                        value="03-02",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/ExampleValue/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                )

                            if embedded_data_specifications is None:
                                embedded_data_specifications = []

                            super().__init__(
                                value=value,
                                id_short=id_short,
                                value_type=value_type,
                                value_id=value_id,
                                display_name=display_name,
                                category=category,
                                description=description,
                                semantic_id=semantic_id,
                                qualifier=qualifier,
                                extension=extension,
                                supplemental_semantic_id=supplemental_semantic_id,
                                embedded_data_specifications=embedded_data_specifications,
                            )

                    class ClassName(MultiLanguageProperty):
                        def __init__(
                            self,
                            value: MultiLanguageTextType,
                            id_short: Optional[str] = "ClassName",
                            value_id: Optional[Reference] = None,
                            display_name: Optional[
                                MultiLanguageNameType
                            ] = MultiLanguageNameType(dict_={"en": "Klassenname"}),
                            category: Optional[str] = "PARAMETER",
                            description: Optional[MultiLanguageTextType] = None,
                            semantic_id: Optional[Reference] = ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="0173-1#02-ABJ219#002",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                            qualifier: Iterable[Qualifier] = None,
                            extension: Iterable[Extension] = (),
                            supplemental_semantic_id: Iterable[Reference] = (
                                ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="https://api.eclass-cdp.com/0173-1-02-ABJ219-002",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                            ),
                            embedded_data_specifications: Iterable[
                                EmbeddedDataSpecification
                            ] = None,
                        ):
                            if qualifier is None:
                                qualifier = (
                                    Qualifier(
                                        type_="SMT/Cardinality",
                                        value_type=str,
                                        value="One",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                    Qualifier(
                                        type_="ExampleValue",
                                        value_type=str,
                                        value="Operation@en",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/ExampleValue/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                )

                            if embedded_data_specifications is None:
                                embedded_data_specifications = []

                            super().__init__(
                                value=value,
                                id_short=id_short,
                                value_id=value_id,
                                display_name=display_name,
                                category=category,
                                description=description,
                                semantic_id=semantic_id,
                                qualifier=qualifier,
                                extension=extension,
                                supplemental_semantic_id=supplemental_semantic_id,
                                embedded_data_specifications=embedded_data_specifications,
                            )

                    class ClassificationSystem(Property):
                        def __init__(
                            self,
                            value: str,
                            id_short: Optional[str] = "ClassificationSystem",
                            value_type: DataTypeDefXsd = str,
                            value_id: Optional[Reference] = None,
                            display_name: Optional[
                                MultiLanguageNameType
                            ] = MultiLanguageNameType(
                                dict_={
                                    "en": "Classification system",
                                    "de": "Klassifizierungssystem",
                                }
                            ),
                            category: Optional[str] = "PARAMETER",
                            description: Optional[MultiLanguageTextType] = None,
                            semantic_id: Optional[Reference] = ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="0173-1#02-ABH997#003",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                            qualifier: Iterable[Qualifier] = None,
                            extension: Iterable[Extension] = (),
                            supplemental_semantic_id: Iterable[Reference] = (
                                ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="https://api.eclass-cdp.com/0173-1-02-ABH997-003",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                            ),
                            embedded_data_specifications: Iterable[
                                EmbeddedDataSpecification
                            ] = None,
                        ):
                            if qualifier is None:
                                qualifier = (
                                    Qualifier(
                                        type_="SMT/Cardinality",
                                        value_type=str,
                                        value="One",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                    Qualifier(
                                        type_="ExampleValue",
                                        value_type=str,
                                        value="VDI2770:2020",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/ExampleValue/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                )

                            if embedded_data_specifications is None:
                                embedded_data_specifications = []

                            super().__init__(
                                value=value,
                                id_short=id_short,
                                value_type=value_type,
                                value_id=value_id,
                                display_name=display_name,
                                category=category,
                                description=description,
                                semantic_id=semantic_id,
                                qualifier=qualifier,
                                extension=extension,
                                supplemental_semantic_id=supplemental_semantic_id,
                                embedded_data_specifications=embedded_data_specifications,
                            )

                    def __init__(
                        self,
                        classId: Union[str, ClassId],
                        className: Union[
                            dict[str, str], MultiLanguageTextType, ClassName
                        ],
                        classificationSystem: Union[str, ClassificationSystem],
                        id_short: Optional[str] = None,
                        display_name: Optional[
                            MultiLanguageNameType
                        ] = MultiLanguageNameType(
                            dict_={
                                "en": "Document classification",
                                "de": "Dokumentklassifikation",
                            }
                        ),
                        category: Optional[str] = None,
                        description: Optional[
                            MultiLanguageTextType
                        ] = MultiLanguageTextType(
                            dict_={
                                "en": "Set of information for describing the classification of the Document according to a ClassificationSystem"
                            }
                        ),
                        semantic_id: Optional[Reference] = ExternalReference(
                            key=(
                                Key(
                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                    value="0173-1#02-ABI502#003/0173-1#01-AHF581#003",
                                ),
                            ),
                            referred_semantic_id=None,
                        ),
                        qualifier: Iterable[Qualifier] = None,
                        extension: Iterable[Extension] = (),
                        supplemental_semantic_id: Iterable[Reference] = (
                            ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="0173-1#02-ABI502#003~0/0173-1#01-AHF581#003",
                                    ),
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="https://api.eclass-cdp.com/0173-1-02-ABI502-003/0173-1-01-AHF581-003",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                        ),
                        embedded_data_specifications: Iterable[
                            EmbeddedDataSpecification
                        ] = None,
                    ):
                        if qualifier is None:
                            qualifier = (
                                Qualifier(
                                    type_="SMT/Cardinality",
                                    value_type=str,
                                    value="OneToMany",
                                    value_id=None,
                                    kind=QualifierKind.CONCEPT_QUALIFIER,
                                    semantic_id=ExternalReference(
                                        key=(
                                            Key(
                                                type_=KeyTypes.GLOBAL_REFERENCE,
                                                value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                            ),
                                        ),
                                        referred_semantic_id=None,
                                    ),
                                    supplemental_semantic_id=(),
                                ),
                            )

                        if embedded_data_specifications is None:
                            embedded_data_specifications = []

                        # Build a submodel element if a raw value was passed in the argument
                        if classId and not isinstance(classId, SubmodelElement):
                            classId = self.ClassId(classId)

                        # Build a submodel element if a raw value was passed in the argument
                        if className and not isinstance(className, SubmodelElement):
                            className = self.ClassName(className)

                        # Build a submodel element if a raw value was passed in the argument
                        if classificationSystem and not isinstance(
                            classificationSystem, SubmodelElement
                        ):
                            classificationSystem = self.ClassificationSystem(
                                classificationSystem
                            )

                        # Add all passed/initialized submodel elements to a single list
                        embedded_submodel_elements = []
                        for se_arg in [classId, className, classificationSystem]:
                            if se_arg is None:
                                continue
                            elif isinstance(se_arg, SubmodelElement):
                                embedded_submodel_elements.append(se_arg)
                            elif isinstance(se_arg, Iterable):
                                for n, element in enumerate(se_arg):
                                    element.id_short = f"{element.id_short}{n}"
                                    embedded_submodel_elements.append(element)
                            else:
                                raise TypeError(
                                    f"Unknown type of value in submodel_element_args: {type(se_arg)}"
                                )

                        super().__init__(
                            value=embedded_submodel_elements,
                            id_short=id_short,
                            display_name=display_name,
                            category=category,
                            description=description,
                            semantic_id=semantic_id,
                            qualifier=qualifier,
                            extension=extension,
                            supplemental_semantic_id=supplemental_semantic_id,
                            embedded_data_specifications=embedded_data_specifications,
                        )

                def __init__(
                    self,
                    documentclassifications_items: Iterable[
                        Documentclassifications_item
                    ],
                    id_short: Optional[str] = "DocumentClassifications",
                    type_value_list_element: SubmodelElement = SubmodelElementCollection,
                    semantic_id_list_element: Optional[Reference] = ExternalReference(
                        key=(
                            Key(
                                type_=KeyTypes.GLOBAL_REFERENCE,
                                value="0173-1#02-ABI502#003/0173-1#01-AHF581#003",
                            ),
                        ),
                        referred_semantic_id=None,
                    ),
                    value_type_list_element: Optional[DataTypeDefXsd] = None,
                    order_relevant: bool = True,
                    display_name: Optional[
                        MultiLanguageNameType
                    ] = MultiLanguageNameType(
                        dict_={
                            "en": "Document classifications",
                            "de": "Dokumentklassifikationen",
                        }
                    ),
                    category: Optional[str] = None,
                    description: Optional[MultiLanguageTextType] = None,
                    semantic_id: Optional[Reference] = ExternalReference(
                        key=(
                            Key(
                                type_=KeyTypes.GLOBAL_REFERENCE,
                                value="0173-1#02-ABI502#003",
                            ),
                        ),
                        referred_semantic_id=None,
                    ),
                    qualifier: Iterable[Qualifier] = None,
                    extension: Iterable[Extension] = (),
                    supplemental_semantic_id: Iterable[Reference] = (
                        ExternalReference(
                            key=(
                                Key(
                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                    value="https://api.eclass-cdp.com/0173-1-02-ABI502-003",
                                ),
                            ),
                            referred_semantic_id=None,
                        ),
                    ),
                    embedded_data_specifications: Iterable[
                        EmbeddedDataSpecification
                    ] = None,
                ):
                    if qualifier is None:
                        qualifier = (
                            Qualifier(
                                type_="SMT/Cardinality",
                                value_type=str,
                                value="One",
                                value_id=None,
                                kind=QualifierKind.CONCEPT_QUALIFIER,
                                semantic_id=ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                                supplemental_semantic_id=(),
                            ),
                        )

                    if embedded_data_specifications is None:
                        embedded_data_specifications = []

                    # Add all passed/initialized submodel elements to a single list
                    embedded_submodel_elements = []
                    for se_arg in [documentclassifications_items]:
                        if se_arg is None:
                            continue
                        elif isinstance(se_arg, SubmodelElement):
                            embedded_submodel_elements.append(se_arg)
                        elif isinstance(se_arg, Iterable):
                            for n, element in enumerate(se_arg):
                                element.id_short = f"{element.id_short}{n}"
                                embedded_submodel_elements.append(element)
                        else:
                            raise TypeError(
                                f"Unknown type of value in submodel_element_args: {type(se_arg)}"
                            )

                    super().__init__(
                        value=embedded_submodel_elements,
                        id_short=id_short,
                        type_value_list_element=type_value_list_element,
                        semantic_id_list_element=semantic_id_list_element,
                        value_type_list_element=value_type_list_element,
                        order_relevant=order_relevant,
                        display_name=display_name,
                        category=category,
                        description=description,
                        semantic_id=semantic_id,
                        qualifier=qualifier,
                        extension=extension,
                        supplemental_semantic_id=supplemental_semantic_id,
                        embedded_data_specifications=embedded_data_specifications,
                    )

                def _check_constraints(self, new, existing) -> None:
                    # Since the id_short contains randomness, unset it temporarily for pretty and predictable error messages.
                    # This also prevents the random id_short from remaining set in case a constraint violation is encountered.
                    saved_id_short = new.id_short
                    new.id_short = None

                    # We relax constraint AASd-108here: It is allowed to add subclasses of the specified in type_value_list_element
                    if not isinstance(new, self.type_value_list_element):
                        raise base.AASConstraintViolation(
                            108,
                            "All first level elements must be of the type specified in "
                            f"type_value_list_element={self.type_value_list_element.__name__}, "
                            f"got {new!r}",
                        )

                    if (
                        self.semantic_id_list_element is not None
                        and new.semantic_id is not None
                        and new.semantic_id != self.semantic_id_list_element
                    ):
                        # Constraint AASd-115 specifies that if the semantic_id of an item is not specified
                        # but semantic_id_list_element is, the semantic_id of the new is assumed to be identical.
                        # Not really a constraint...
                        # TODO: maybe set the semantic_id of new to semantic_id_list_element if it is None
                        raise base.AASConstraintViolation(
                            107,
                            f"If semantic_id_list_element={self.semantic_id_list_element!r} "
                            "is specified all first level children must have the same "
                            f"semantic_id, got {new!r} with semantic_id={new.semantic_id!r}",
                        )

                    # If we got here we know that `new` is an instance of type_value_list_element and that type_value_list_element
                    # is either Property or Range. Thus, `new` must have the value_type property.
                    # Furthermore, value_type_list_element cannot be None, as this is already checked in __init__().
                    if (
                        isinstance(self.type_value_list_element, Property)
                        or isinstance(self.type_value_list_element, Range)
                        and not isinstance(new.value_type, self.value_type_list_element)
                    ):  # type: ignore
                        raise base.AASConstraintViolation(
                            109,
                            "All first level elements must have the value_type "  # type: ignore
                            "specified by value_type_list_element="
                            f"{self.value_type_list_element.__name__}, got "  # type: ignore
                            f"{new!r} with value_type={new.value_type.__name__}",
                        )  # type: ignore

                    # If semantic_id_list_element is not None that would already enforce the semantic_id for all first level
                    # elements. Thus, we only need to perform this check if semantic_id_list_element is None.
                    if (
                        new.semantic_id is not None
                        and self.semantic_id_list_element is None
                    ):
                        for item in existing:
                            if (
                                item.semantic_id is not None
                                and new.semantic_id != item.semantic_id
                            ):
                                raise base.AASConstraintViolation(
                                    114,
                                    f"Element to be added {new!r} has semantic_id "
                                    f"{new.semantic_id!r}, while already contained element "
                                    f"{item!r} has semantic_id {item.semantic_id!r}, which "
                                    "aren't equal.",
                                )

                    # Re-assign id_short
                    new.id_short = saved_id_short

            class DocumentVersions(SubmodelElementList):
                class Documentversions_item(SubmodelElementCollection):
                    class Language(SubmodelElementList):
                        class Language_item(Property):
                            def __init__(
                                self,
                                value: str,
                                id_short: Optional[str] = None,
                                value_type: DataTypeDefXsd = str,
                                value_id: Optional[Reference] = ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="0173-1#07-AAS045#003",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                                display_name: Optional[
                                    MultiLanguageNameType
                                ] = MultiLanguageNameType(
                                    dict_={"en": "en (English)", "de": "en (Englisch)"}
                                ),
                                category: Optional[str] = None,
                                description: Optional[MultiLanguageTextType] = None,
                                semantic_id: Optional[Reference] = ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="0173-1#02-AAN468#008",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                                qualifier: Iterable[Qualifier] = None,
                                extension: Iterable[Extension] = (),
                                supplemental_semantic_id: Iterable[Reference] = (),
                                embedded_data_specifications: Iterable[
                                    EmbeddedDataSpecification
                                ] = None,
                            ):
                                if qualifier is None:
                                    qualifier = (
                                        Qualifier(
                                            type_="SMT/Cardinality",
                                            value_type=str,
                                            value="OneToMany",
                                            value_id=None,
                                            kind=QualifierKind.CONCEPT_QUALIFIER,
                                            semantic_id=ExternalReference(
                                                key=(
                                                    Key(
                                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                                        value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                                    ),
                                                ),
                                                referred_semantic_id=None,
                                            ),
                                            supplemental_semantic_id=(),
                                        ),
                                        Qualifier(
                                            type_="ExampleValue",
                                            value_type=str,
                                            value="en",
                                            value_id=None,
                                            kind=QualifierKind.CONCEPT_QUALIFIER,
                                            semantic_id=ExternalReference(
                                                key=(
                                                    Key(
                                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                                        value="https://admin-shell.io/SubmodelTemplates/ExampleValue/1/0",
                                                    ),
                                                ),
                                                referred_semantic_id=None,
                                            ),
                                            supplemental_semantic_id=(),
                                        ),
                                    )

                                if embedded_data_specifications is None:
                                    embedded_data_specifications = []

                                super().__init__(
                                    value=value,
                                    id_short=id_short,
                                    value_type=value_type,
                                    value_id=value_id,
                                    display_name=display_name,
                                    category=category,
                                    description=description,
                                    semantic_id=semantic_id,
                                    qualifier=qualifier,
                                    extension=extension,
                                    supplemental_semantic_id=supplemental_semantic_id,
                                    embedded_data_specifications=embedded_data_specifications,
                                )

                        def __init__(
                            self,
                            language_items: Iterable[Union[str, Language_item]],
                            id_short: Optional[str] = "Language",
                            type_value_list_element: SubmodelElement = Property,
                            semantic_id_list_element: Optional[Reference] = None,
                            value_type_list_element: Optional[DataTypeDefXsd] = str,
                            order_relevant: bool = True,
                            display_name: Optional[
                                MultiLanguageNameType
                            ] = MultiLanguageNameType(
                                dict_={"en": "Language", "de": "Sprache"}
                            ),
                            category: Optional[str] = None,
                            description: Optional[MultiLanguageTextType] = None,
                            semantic_id: Optional[Reference] = ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="0173-1#02-AAN468#008",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                            qualifier: Iterable[Qualifier] = None,
                            extension: Iterable[Extension] = (),
                            supplemental_semantic_id: Iterable[Reference] = (
                                ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="https://api.eclass-cdp.com/0173-1-02-AAN468-008",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                            ),
                            embedded_data_specifications: Iterable[
                                EmbeddedDataSpecification
                            ] = None,
                        ):
                            if qualifier is None:
                                qualifier = (
                                    Qualifier(
                                        type_="SMT/Cardinality",
                                        value_type=str,
                                        value="One",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                )

                            if embedded_data_specifications is None:
                                embedded_data_specifications = []

                            # Build a list of submodel elements if a raw values were passed in the argument
                            if language_items and all(
                                [isinstance(i, str) for i in language_items]
                            ):
                                language_items = [
                                    self.Language_item(i) for i in language_items
                                ]

                            # Add all passed/initialized submodel elements to a single list
                            embedded_submodel_elements = []
                            for se_arg in [language_items]:
                                if se_arg is None:
                                    continue
                                elif isinstance(se_arg, SubmodelElement):
                                    embedded_submodel_elements.append(se_arg)
                                elif isinstance(se_arg, Iterable):
                                    for n, element in enumerate(se_arg):
                                        element.id_short = f"{element.id_short}{n}"
                                        embedded_submodel_elements.append(element)
                                else:
                                    raise TypeError(
                                        f"Unknown type of value in submodel_element_args: {type(se_arg)}"
                                    )

                            super().__init__(
                                value=embedded_submodel_elements,
                                id_short=id_short,
                                type_value_list_element=type_value_list_element,
                                semantic_id_list_element=semantic_id_list_element,
                                value_type_list_element=value_type_list_element,
                                order_relevant=order_relevant,
                                display_name=display_name,
                                category=category,
                                description=description,
                                semantic_id=semantic_id,
                                qualifier=qualifier,
                                extension=extension,
                                supplemental_semantic_id=supplemental_semantic_id,
                                embedded_data_specifications=embedded_data_specifications,
                            )

                        def _check_constraints(self, new, existing) -> None:
                            # Since the id_short contains randomness, unset it temporarily for pretty and predictable error messages.
                            # This also prevents the random id_short from remaining set in case a constraint violation is encountered.
                            saved_id_short = new.id_short
                            new.id_short = None

                            # We relax constraint AASd-108here: It is allowed to add subclasses of the specified in type_value_list_element
                            if not isinstance(new, self.type_value_list_element):
                                raise base.AASConstraintViolation(
                                    108,
                                    "All first level elements must be of the type specified in "
                                    f"type_value_list_element={self.type_value_list_element.__name__}, "
                                    f"got {new!r}",
                                )

                            if (
                                self.semantic_id_list_element is not None
                                and new.semantic_id is not None
                                and new.semantic_id != self.semantic_id_list_element
                            ):
                                # Constraint AASd-115 specifies that if the semantic_id of an item is not specified
                                # but semantic_id_list_element is, the semantic_id of the new is assumed to be identical.
                                # Not really a constraint...
                                # TODO: maybe set the semantic_id of new to semantic_id_list_element if it is None
                                raise base.AASConstraintViolation(
                                    107,
                                    f"If semantic_id_list_element={self.semantic_id_list_element!r} "
                                    "is specified all first level children must have the same "
                                    f"semantic_id, got {new!r} with semantic_id={new.semantic_id!r}",
                                )

                            # If we got here we know that `new` is an instance of type_value_list_element and that type_value_list_element
                            # is either Property or Range. Thus, `new` must have the value_type property.
                            # Furthermore, value_type_list_element cannot be None, as this is already checked in __init__().
                            if (
                                isinstance(self.type_value_list_element, Property)
                                or isinstance(self.type_value_list_element, Range)
                                and not isinstance(
                                    new.value_type, self.value_type_list_element
                                )
                            ):  # type: ignore
                                raise base.AASConstraintViolation(
                                    109,
                                    "All first level elements must have the value_type "  # type: ignore
                                    "specified by value_type_list_element="
                                    f"{self.value_type_list_element.__name__}, got "  # type: ignore
                                    f"{new!r} with value_type={new.value_type.__name__}",
                                )  # type: ignore

                            # If semantic_id_list_element is not None that would already enforce the semantic_id for all first level
                            # elements. Thus, we only need to perform this check if semantic_id_list_element is None.
                            if (
                                new.semantic_id is not None
                                and self.semantic_id_list_element is None
                            ):
                                for item in existing:
                                    if (
                                        item.semantic_id is not None
                                        and new.semantic_id != item.semantic_id
                                    ):
                                        raise base.AASConstraintViolation(
                                            114,
                                            f"Element to be added {new!r} has semantic_id "
                                            f"{new.semantic_id!r}, while already contained element "
                                            f"{item!r} has semantic_id {item.semantic_id!r}, which "
                                            "aren't equal.",
                                        )

                            # Re-assign id_short
                            new.id_short = saved_id_short

                    class Version(Property):
                        def __init__(
                            self,
                            value: str,
                            id_short: Optional[str] = "Version",
                            value_type: DataTypeDefXsd = str,
                            value_id: Optional[Reference] = None,
                            display_name: Optional[
                                MultiLanguageNameType
                            ] = MultiLanguageNameType(
                                dict_={
                                    "en": "Document version",
                                    "de": "Dokumentenversion",
                                }
                            ),
                            category: Optional[str] = "PARAMETER",
                            description: Optional[MultiLanguageTextType] = None,
                            semantic_id: Optional[Reference] = ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="0173-1#02-AAP003#005",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                            qualifier: Iterable[Qualifier] = None,
                            extension: Iterable[Extension] = (),
                            supplemental_semantic_id: Iterable[Reference] = (
                                ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="https://api.eclass-cdp.com/0173-1-02-AAP003-005",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                            ),
                            embedded_data_specifications: Iterable[
                                EmbeddedDataSpecification
                            ] = None,
                        ):
                            if qualifier is None:
                                qualifier = (
                                    Qualifier(
                                        type_="SMT/Cardinality",
                                        value_type=str,
                                        value="One",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                    Qualifier(
                                        type_="ExampleValue",
                                        value_type=str,
                                        value="V1.2",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/ExampleValue/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                )

                            if embedded_data_specifications is None:
                                embedded_data_specifications = []

                            super().__init__(
                                value=value,
                                id_short=id_short,
                                value_type=value_type,
                                value_id=value_id,
                                display_name=display_name,
                                category=category,
                                description=description,
                                semantic_id=semantic_id,
                                qualifier=qualifier,
                                extension=extension,
                                supplemental_semantic_id=supplemental_semantic_id,
                                embedded_data_specifications=embedded_data_specifications,
                            )

                    class Title(MultiLanguageProperty):
                        def __init__(
                            self,
                            value: MultiLanguageTextType,
                            id_short: Optional[str] = "Title",
                            value_id: Optional[Reference] = None,
                            display_name: Optional[
                                MultiLanguageNameType
                            ] = MultiLanguageNameType(
                                dict_={"en": "Document title", "de": "Dokumententitel"}
                            ),
                            category: Optional[str] = "PARAMETER",
                            description: Optional[MultiLanguageTextType] = None,
                            semantic_id: Optional[Reference] = ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="0173-1#02-ABG940#003",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                            qualifier: Iterable[Qualifier] = None,
                            extension: Iterable[Extension] = (),
                            supplemental_semantic_id: Iterable[Reference] = (
                                ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="https://api.eclass-cdp.com/0173-1-02-ABG940-003",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                            ),
                            embedded_data_specifications: Iterable[
                                EmbeddedDataSpecification
                            ] = None,
                        ):
                            if qualifier is None:
                                qualifier = (
                                    Qualifier(
                                        type_="SMT/Cardinality",
                                        value_type=str,
                                        value="One",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                    Qualifier(
                                        type_="ExampleValue",
                                        value_type=str,
                                        value="Examplary title@en",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/ExampleValue/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                )

                            if embedded_data_specifications is None:
                                embedded_data_specifications = []

                            super().__init__(
                                value=value,
                                id_short=id_short,
                                value_id=value_id,
                                display_name=display_name,
                                category=category,
                                description=description,
                                semantic_id=semantic_id,
                                qualifier=qualifier,
                                extension=extension,
                                supplemental_semantic_id=supplemental_semantic_id,
                                embedded_data_specifications=embedded_data_specifications,
                            )

                    class Subtitle(MultiLanguageProperty):
                        def __init__(
                            self,
                            value: MultiLanguageTextType,
                            id_short: Optional[str] = "Subtitle",
                            value_id: Optional[Reference] = None,
                            display_name: Optional[
                                MultiLanguageNameType
                            ] = MultiLanguageNameType(
                                dict_={"en": "Subtitle", "de": "Untertitel"}
                            ),
                            category: Optional[str] = "PARAMETER",
                            description: Optional[MultiLanguageTextType] = None,
                            semantic_id: Optional[Reference] = ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="0173-1#02-ABH998#003",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                            qualifier: Iterable[Qualifier] = None,
                            extension: Iterable[Extension] = (),
                            supplemental_semantic_id: Iterable[Reference] = (
                                ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="https://api.eclass-cdp.com/0173-1-02-ABH998-003",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                            ),
                            embedded_data_specifications: Iterable[
                                EmbeddedDataSpecification
                            ] = None,
                        ):
                            if qualifier is None:
                                qualifier = (
                                    Qualifier(
                                        type_="SMT/Cardinality",
                                        value_type=str,
                                        value="ZeroToOne",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                    Qualifier(
                                        type_="ExampleValue",
                                        value_type=str,
                                        value="Examplary subtitle@en",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/ExampleValue/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                )

                            if embedded_data_specifications is None:
                                embedded_data_specifications = []

                            super().__init__(
                                value=value,
                                id_short=id_short,
                                value_id=value_id,
                                display_name=display_name,
                                category=category,
                                description=description,
                                semantic_id=semantic_id,
                                qualifier=qualifier,
                                extension=extension,
                                supplemental_semantic_id=supplemental_semantic_id,
                                embedded_data_specifications=embedded_data_specifications,
                            )

                    class Description(MultiLanguageProperty):
                        def __init__(
                            self,
                            value: MultiLanguageTextType,
                            id_short: Optional[str] = "Description",
                            value_id: Optional[Reference] = None,
                            display_name: Optional[
                                MultiLanguageNameType
                            ] = MultiLanguageNameType(
                                dict_={
                                    "en": "Document description",
                                    "de": "Dokumentenbeschreibung",
                                }
                            ),
                            category: Optional[str] = "PARAMETER",
                            description: Optional[MultiLanguageTextType] = None,
                            semantic_id: Optional[Reference] = ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="0173-1#02-AAN466#004",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                            qualifier: Iterable[Qualifier] = None,
                            extension: Iterable[Extension] = (),
                            supplemental_semantic_id: Iterable[Reference] = (
                                ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="https://api.eclass-cdp.com/0173-1-02-AAN466-004",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                            ),
                            embedded_data_specifications: Iterable[
                                EmbeddedDataSpecification
                            ] = None,
                        ):
                            if qualifier is None:
                                qualifier = (
                                    Qualifier(
                                        type_="SMT/Cardinality",
                                        value_type=str,
                                        value="One",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                    Qualifier(
                                        type_="ExampleValue",
                                        value_type=str,
                                        value="Abstract@en",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/ExampleValue/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                )

                            if embedded_data_specifications is None:
                                embedded_data_specifications = []

                            super().__init__(
                                value=value,
                                id_short=id_short,
                                value_id=value_id,
                                display_name=display_name,
                                category=category,
                                description=description,
                                semantic_id=semantic_id,
                                qualifier=qualifier,
                                extension=extension,
                                supplemental_semantic_id=supplemental_semantic_id,
                                embedded_data_specifications=embedded_data_specifications,
                            )

                    class KeyWords(MultiLanguageProperty):
                        def __init__(
                            self,
                            value: MultiLanguageTextType,
                            id_short: Optional[str] = "KeyWords",
                            value_id: Optional[Reference] = None,
                            display_name: Optional[
                                MultiLanguageNameType
                            ] = MultiLanguageNameType(
                                dict_={"en": "Keywords", "de": "Stichworte"}
                            ),
                            category: Optional[str] = "PARAMETER",
                            description: Optional[MultiLanguageTextType] = None,
                            semantic_id: Optional[Reference] = ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="0173-1#02-ABH999#003",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                            qualifier: Iterable[Qualifier] = None,
                            extension: Iterable[Extension] = (),
                            supplemental_semantic_id: Iterable[Reference] = (
                                ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="https://api.eclass-cdp.com/0173-1-02-ABH999-003",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                            ),
                            embedded_data_specifications: Iterable[
                                EmbeddedDataSpecification
                            ] = None,
                        ):
                            if qualifier is None:
                                qualifier = (
                                    Qualifier(
                                        type_="SMT/Cardinality",
                                        value_type=str,
                                        value="ZeroToOne",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                    Qualifier(
                                        type_="ExampleValue",
                                        value_type=str,
                                        value="Examplary keywords@en",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/ExampleValue/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                )

                            if embedded_data_specifications is None:
                                embedded_data_specifications = []

                            super().__init__(
                                value=value,
                                id_short=id_short,
                                value_id=value_id,
                                display_name=display_name,
                                category=category,
                                description=description,
                                semantic_id=semantic_id,
                                qualifier=qualifier,
                                extension=extension,
                                supplemental_semantic_id=supplemental_semantic_id,
                                embedded_data_specifications=embedded_data_specifications,
                            )

                    class StatusSetDate(Property):
                        def __init__(
                            self,
                            value: Date,
                            id_short: Optional[str] = "StatusSetDate",
                            value_type: DataTypeDefXsd = Date,
                            value_id: Optional[Reference] = None,
                            display_name: Optional[
                                MultiLanguageNameType
                            ] = MultiLanguageNameType(
                                dict_={
                                    "en": "Document status set date",
                                    "de": "Datum der Einstellung des Dokumentenstatus",
                                }
                            ),
                            category: Optional[str] = "PARAMETER",
                            description: Optional[MultiLanguageTextType] = None,
                            semantic_id: Optional[Reference] = ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="0173-1#02-ABI000#003",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                            qualifier: Iterable[Qualifier] = None,
                            extension: Iterable[Extension] = (),
                            supplemental_semantic_id: Iterable[Reference] = (
                                ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="https://api.eclass-cdp.com/0173-1-02-ABI000-003",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                            ),
                            embedded_data_specifications: Iterable[
                                EmbeddedDataSpecification
                            ] = None,
                        ):
                            if qualifier is None:
                                qualifier = (
                                    Qualifier(
                                        type_="SMT/Cardinality",
                                        value_type=str,
                                        value="One",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                    Qualifier(
                                        type_="ExampleValue",
                                        value_type=str,
                                        value="2020-02-06",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/ExampleValue/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                )

                            if embedded_data_specifications is None:
                                embedded_data_specifications = []

                            super().__init__(
                                value=value,
                                id_short=id_short,
                                value_type=value_type,
                                value_id=value_id,
                                display_name=display_name,
                                category=category,
                                description=description,
                                semantic_id=semantic_id,
                                qualifier=qualifier,
                                extension=extension,
                                supplemental_semantic_id=supplemental_semantic_id,
                                embedded_data_specifications=embedded_data_specifications,
                            )

                    class StatusValue(Property):
                        def __init__(
                            self,
                            value: str,
                            id_short: Optional[str] = "StatusValue",
                            value_type: DataTypeDefXsd = str,
                            value_id: Optional[Reference] = None,
                            display_name: Optional[
                                MultiLanguageNameType
                            ] = MultiLanguageNameType(
                                dict_={"en": "Document status", "de": "Dokumentstatus"}
                            ),
                            category: Optional[str] = "PARAMETER",
                            description: Optional[MultiLanguageTextType] = None,
                            semantic_id: Optional[Reference] = ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="0173-1#02-ABI001#003",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                            qualifier: Iterable[Qualifier] = None,
                            extension: Iterable[Extension] = (),
                            supplemental_semantic_id: Iterable[Reference] = (
                                ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="https://api.eclass-cdp.com/0173-1-02-ABI001-003",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                            ),
                            embedded_data_specifications: Iterable[
                                EmbeddedDataSpecification
                            ] = None,
                        ):
                            if qualifier is None:
                                qualifier = (
                                    Qualifier(
                                        type_="SMT/Cardinality",
                                        value_type=str,
                                        value="One",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                    Qualifier(
                                        type_="ExampleValue",
                                        value_type=str,
                                        value="Released",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/ExampleValue/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                )

                            if embedded_data_specifications is None:
                                embedded_data_specifications = []

                            super().__init__(
                                value=value,
                                id_short=id_short,
                                value_type=value_type,
                                value_id=value_id,
                                display_name=display_name,
                                category=category,
                                description=description,
                                semantic_id=semantic_id,
                                qualifier=qualifier,
                                extension=extension,
                                supplemental_semantic_id=supplemental_semantic_id,
                                embedded_data_specifications=embedded_data_specifications,
                            )

                    class OrganizationShortName(Property):
                        def __init__(
                            self,
                            value: str,
                            id_short: Optional[str] = "OrganizationShortName",
                            value_type: DataTypeDefXsd = str,
                            value_id: Optional[Reference] = None,
                            display_name: Optional[
                                MultiLanguageNameType
                            ] = MultiLanguageNameType(
                                dict_={
                                    "en": "Organization short name",
                                    "de": "Kurzname der Organisation",
                                }
                            ),
                            category: Optional[str] = "PARAMETER",
                            description: Optional[MultiLanguageTextType] = None,
                            semantic_id: Optional[Reference] = ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="https://api.eclass-cdp.com/0173-1-02-ABI002-003",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                            qualifier: Iterable[Qualifier] = None,
                            extension: Iterable[Extension] = (),
                            supplemental_semantic_id: Iterable[Reference] = (),
                            embedded_data_specifications: Iterable[
                                EmbeddedDataSpecification
                            ] = None,
                        ):
                            if qualifier is None:
                                qualifier = (
                                    Qualifier(
                                        type_="SMT/Cardinality",
                                        value_type=str,
                                        value="One",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                    Qualifier(
                                        type_="ExampleValue",
                                        value_type=str,
                                        value="Example company",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/ExampleValue/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                )

                            if embedded_data_specifications is None:
                                embedded_data_specifications = []

                            super().__init__(
                                value=value,
                                id_short=id_short,
                                value_type=value_type,
                                value_id=value_id,
                                display_name=display_name,
                                category=category,
                                description=description,
                                semantic_id=semantic_id,
                                qualifier=qualifier,
                                extension=extension,
                                supplemental_semantic_id=supplemental_semantic_id,
                                embedded_data_specifications=embedded_data_specifications,
                            )

                    class OrganizationOfficialName(Property):
                        def __init__(
                            self,
                            value: str,
                            id_short: Optional[str] = "OrganizationOfficialName",
                            value_type: DataTypeDefXsd = str,
                            value_id: Optional[Reference] = None,
                            display_name: Optional[
                                MultiLanguageNameType
                            ] = MultiLanguageNameType(
                                dict_={
                                    "en": "Organization official name",
                                    "de": "Offizieller Name der Organisation",
                                }
                            ),
                            category: Optional[str] = "PARAMETER",
                            description: Optional[MultiLanguageTextType] = None,
                            semantic_id: Optional[Reference] = ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="0173-1#02-ABI004#003",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                            qualifier: Iterable[Qualifier] = None,
                            extension: Iterable[Extension] = (),
                            supplemental_semantic_id: Iterable[Reference] = (
                                ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="https://api.eclass-cdp.com/0173-1-02-ABI004-003",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                            ),
                            embedded_data_specifications: Iterable[
                                EmbeddedDataSpecification
                            ] = None,
                        ):
                            if qualifier is None:
                                qualifier = (
                                    Qualifier(
                                        type_="SMT/Cardinality",
                                        value_type=str,
                                        value="One",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                    Qualifier(
                                        type_="ExampleValue",
                                        value_type=str,
                                        value="Example company Ltd.",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/ExampleValue/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                )

                            if embedded_data_specifications is None:
                                embedded_data_specifications = []

                            super().__init__(
                                value=value,
                                id_short=id_short,
                                value_type=value_type,
                                value_id=value_id,
                                display_name=display_name,
                                category=category,
                                description=description,
                                semantic_id=semantic_id,
                                qualifier=qualifier,
                                extension=extension,
                                supplemental_semantic_id=supplemental_semantic_id,
                                embedded_data_specifications=embedded_data_specifications,
                            )

                    class RefersToEntities(SubmodelElementList):
                        class Referstoentities_item(ReferenceElement):
                            def __init__(
                                self,
                                value: Reference,
                                id_short: Optional[str] = None,
                                display_name: Optional[MultiLanguageNameType] = None,
                                category: Optional[str] = "PARAMETER",
                                description: Optional[MultiLanguageTextType] = None,
                                semantic_id: Optional[Reference] = ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="0173-1#02-ABK288#002",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                                qualifier: Iterable[Qualifier] = None,
                                extension: Iterable[Extension] = (),
                                supplemental_semantic_id: Iterable[Reference] = (),
                                embedded_data_specifications: Iterable[
                                    EmbeddedDataSpecification
                                ] = None,
                            ):
                                if qualifier is None:
                                    qualifier = (
                                        Qualifier(
                                            type_="SMT/Cardinality",
                                            value_type=str,
                                            value="OneToMany",
                                            value_id=None,
                                            kind=QualifierKind.CONCEPT_QUALIFIER,
                                            semantic_id=ExternalReference(
                                                key=(
                                                    Key(
                                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                                        value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                                    ),
                                                ),
                                                referred_semantic_id=None,
                                            ),
                                            supplemental_semantic_id=(),
                                        ),
                                        Qualifier(
                                            type_="AllowedIdShort",
                                            value_type=str,
                                            value="RefersTo[\d{2,3}]",
                                            value_id=None,
                                            kind=QualifierKind.CONCEPT_QUALIFIER,
                                            semantic_id=ExternalReference(
                                                key=(
                                                    Key(
                                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                                        value="https://admin-shell.io/SubmodelTemplates/AllowedIdShort/1/0",
                                                    ),
                                                ),
                                                referred_semantic_id=None,
                                            ),
                                            supplemental_semantic_id=(),
                                        ),
                                    )

                                if embedded_data_specifications is None:
                                    embedded_data_specifications = []

                                super().__init__(
                                    value=value,
                                    id_short=id_short,
                                    display_name=display_name,
                                    category=category,
                                    description=description,
                                    semantic_id=semantic_id,
                                    qualifier=qualifier,
                                    extension=extension,
                                    supplemental_semantic_id=supplemental_semantic_id,
                                    embedded_data_specifications=embedded_data_specifications,
                                )

                        def __init__(
                            self,
                            referstoentities_items: Iterable[
                                Union[Reference, Referstoentities_item]
                            ],
                            id_short: Optional[str] = "RefersToEntities",
                            type_value_list_element: SubmodelElement = ReferenceElement,
                            semantic_id_list_element: Optional[Reference] = None,
                            value_type_list_element: Optional[DataTypeDefXsd] = None,
                            order_relevant: bool = True,
                            display_name: Optional[
                                MultiLanguageNameType
                            ] = MultiLanguageNameType(
                                dict_={
                                    "en": "Reference to other documents",
                                    "de": "Referenz zu anderen Dokumenten",
                                }
                            ),
                            category: Optional[str] = None,
                            description: Optional[MultiLanguageTextType] = None,
                            semantic_id: Optional[Reference] = ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="0173-1#02-ABK288#002",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                            qualifier: Iterable[Qualifier] = None,
                            extension: Iterable[Extension] = (),
                            supplemental_semantic_id: Iterable[Reference] = (
                                ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="https://api.eclass-cdp.com/0173-1-02-ABK288-002",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                            ),
                            embedded_data_specifications: Iterable[
                                EmbeddedDataSpecification
                            ] = None,
                        ):
                            if qualifier is None:
                                qualifier = (
                                    Qualifier(
                                        type_="SMT/Cardinality",
                                        value_type=str,
                                        value="ZeroToOne",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/ExampleValue/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                )

                            if embedded_data_specifications is None:
                                embedded_data_specifications = []

                            # Build a list of submodel elements if a raw values were passed in the argument
                            if referstoentities_items and all(
                                [
                                    isinstance(i, Reference)
                                    for i in referstoentities_items
                                ]
                            ):
                                referstoentities_items = [
                                    self.Referstoentities_item(i)
                                    for i in referstoentities_items
                                ]

                            # Add all passed/initialized submodel elements to a single list
                            embedded_submodel_elements = []
                            for se_arg in [referstoentities_items]:
                                if se_arg is None:
                                    continue
                                elif isinstance(se_arg, SubmodelElement):
                                    embedded_submodel_elements.append(se_arg)
                                elif isinstance(se_arg, Iterable):
                                    for n, element in enumerate(se_arg):
                                        element.id_short = f"{element.id_short}{n}"
                                        embedded_submodel_elements.append(element)
                                else:
                                    raise TypeError(
                                        f"Unknown type of value in submodel_element_args: {type(se_arg)}"
                                    )

                            super().__init__(
                                value=embedded_submodel_elements,
                                id_short=id_short,
                                type_value_list_element=type_value_list_element,
                                semantic_id_list_element=semantic_id_list_element,
                                value_type_list_element=value_type_list_element,
                                order_relevant=order_relevant,
                                display_name=display_name,
                                category=category,
                                description=description,
                                semantic_id=semantic_id,
                                qualifier=qualifier,
                                extension=extension,
                                supplemental_semantic_id=supplemental_semantic_id,
                                embedded_data_specifications=embedded_data_specifications,
                            )

                        def _check_constraints(self, new, existing) -> None:
                            # Since the id_short contains randomness, unset it temporarily for pretty and predictable error messages.
                            # This also prevents the random id_short from remaining set in case a constraint violation is encountered.
                            saved_id_short = new.id_short
                            new.id_short = None

                            # We relax constraint AASd-108here: It is allowed to add subclasses of the specified in type_value_list_element
                            if not isinstance(new, self.type_value_list_element):
                                raise base.AASConstraintViolation(
                                    108,
                                    "All first level elements must be of the type specified in "
                                    f"type_value_list_element={self.type_value_list_element.__name__}, "
                                    f"got {new!r}",
                                )

                            if (
                                self.semantic_id_list_element is not None
                                and new.semantic_id is not None
                                and new.semantic_id != self.semantic_id_list_element
                            ):
                                # Constraint AASd-115 specifies that if the semantic_id of an item is not specified
                                # but semantic_id_list_element is, the semantic_id of the new is assumed to be identical.
                                # Not really a constraint...
                                # TODO: maybe set the semantic_id of new to semantic_id_list_element if it is None
                                raise base.AASConstraintViolation(
                                    107,
                                    f"If semantic_id_list_element={self.semantic_id_list_element!r} "
                                    "is specified all first level children must have the same "
                                    f"semantic_id, got {new!r} with semantic_id={new.semantic_id!r}",
                                )

                            # If we got here we know that `new` is an instance of type_value_list_element and that type_value_list_element
                            # is either Property or Range. Thus, `new` must have the value_type property.
                            # Furthermore, value_type_list_element cannot be None, as this is already checked in __init__().
                            if (
                                isinstance(self.type_value_list_element, Property)
                                or isinstance(self.type_value_list_element, Range)
                                and not isinstance(
                                    new.value_type, self.value_type_list_element
                                )
                            ):  # type: ignore
                                raise base.AASConstraintViolation(
                                    109,
                                    "All first level elements must have the value_type "  # type: ignore
                                    "specified by value_type_list_element="
                                    f"{self.value_type_list_element.__name__}, got "  # type: ignore
                                    f"{new!r} with value_type={new.value_type.__name__}",
                                )  # type: ignore

                            # If semantic_id_list_element is not None that would already enforce the semantic_id for all first level
                            # elements. Thus, we only need to perform this check if semantic_id_list_element is None.
                            if (
                                new.semantic_id is not None
                                and self.semantic_id_list_element is None
                            ):
                                for item in existing:
                                    if (
                                        item.semantic_id is not None
                                        and new.semantic_id != item.semantic_id
                                    ):
                                        raise base.AASConstraintViolation(
                                            114,
                                            f"Element to be added {new!r} has semantic_id "
                                            f"{new.semantic_id!r}, while already contained element "
                                            f"{item!r} has semantic_id {item.semantic_id!r}, which "
                                            "aren't equal.",
                                        )

                            # Re-assign id_short
                            new.id_short = saved_id_short

                    class BasedOnReferences(SubmodelElementList):
                        class Basedonreferences_item(ReferenceElement):
                            def __init__(
                                self,
                                value: Reference,
                                id_short: Optional[str] = None,
                                display_name: Optional[MultiLanguageNameType] = None,
                                category: Optional[str] = "PARAMETER",
                                description: Optional[MultiLanguageTextType] = None,
                                semantic_id: Optional[Reference] = ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="0173-1#02-ABK289#002",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                                qualifier: Iterable[Qualifier] = None,
                                extension: Iterable[Extension] = (),
                                supplemental_semantic_id: Iterable[Reference] = (),
                                embedded_data_specifications: Iterable[
                                    EmbeddedDataSpecification
                                ] = None,
                            ):
                                if qualifier is None:
                                    qualifier = (
                                        Qualifier(
                                            type_="SMT/Cardinality",
                                            value_type=str,
                                            value="OneToMany",
                                            value_id=None,
                                            kind=QualifierKind.CONCEPT_QUALIFIER,
                                            semantic_id=ExternalReference(
                                                key=(
                                                    Key(
                                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                                        value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                                    ),
                                                ),
                                                referred_semantic_id=None,
                                            ),
                                            supplemental_semantic_id=(),
                                        ),
                                        Qualifier(
                                            type_="AllowedIdShort",
                                            value_type=str,
                                            value="BasedOn[\d{2,3}]",
                                            value_id=None,
                                            kind=QualifierKind.CONCEPT_QUALIFIER,
                                            semantic_id=ExternalReference(
                                                key=(
                                                    Key(
                                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                                        value="https://admin-shell.io/SubmodelTemplates/AllowedIdShort/1/0",
                                                    ),
                                                ),
                                                referred_semantic_id=None,
                                            ),
                                            supplemental_semantic_id=(),
                                        ),
                                    )

                                if embedded_data_specifications is None:
                                    embedded_data_specifications = []

                                super().__init__(
                                    value=value,
                                    id_short=id_short,
                                    display_name=display_name,
                                    category=category,
                                    description=description,
                                    semantic_id=semantic_id,
                                    qualifier=qualifier,
                                    extension=extension,
                                    supplemental_semantic_id=supplemental_semantic_id,
                                    embedded_data_specifications=embedded_data_specifications,
                                )

                        def __init__(
                            self,
                            basedonreferences_items: Iterable[
                                Union[Reference, Basedonreferences_item]
                            ],
                            id_short: Optional[str] = "BasedOnReferences",
                            type_value_list_element: SubmodelElement = ReferenceElement,
                            semantic_id_list_element: Optional[Reference] = None,
                            value_type_list_element: Optional[DataTypeDefXsd] = None,
                            order_relevant: bool = True,
                            display_name: Optional[
                                MultiLanguageNameType
                            ] = MultiLanguageNameType(
                                dict_={
                                    "en": "Based on other documents",
                                    "de": "Basiert auf anderen Dokumenten",
                                }
                            ),
                            category: Optional[str] = None,
                            description: Optional[MultiLanguageTextType] = None,
                            semantic_id: Optional[Reference] = ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="0173-1#02-ABK289#002",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                            qualifier: Iterable[Qualifier] = None,
                            extension: Iterable[Extension] = (),
                            supplemental_semantic_id: Iterable[Reference] = (
                                ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="https://api.eclass-cdp.com/0173-1-02-ABK289-002",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                            ),
                            embedded_data_specifications: Iterable[
                                EmbeddedDataSpecification
                            ] = None,
                        ):
                            if qualifier is None:
                                qualifier = (
                                    Qualifier(
                                        type_="SMT/Cardinality",
                                        value_type=str,
                                        value="ZeroToOne",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/ExampleValue/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                )

                            if embedded_data_specifications is None:
                                embedded_data_specifications = []

                            # Build a list of submodel elements if a raw values were passed in the argument
                            if basedonreferences_items and all(
                                [
                                    isinstance(i, Reference)
                                    for i in basedonreferences_items
                                ]
                            ):
                                basedonreferences_items = [
                                    self.Basedonreferences_item(i)
                                    for i in basedonreferences_items
                                ]

                            # Add all passed/initialized submodel elements to a single list
                            embedded_submodel_elements = []
                            for se_arg in [basedonreferences_items]:
                                if se_arg is None:
                                    continue
                                elif isinstance(se_arg, SubmodelElement):
                                    embedded_submodel_elements.append(se_arg)
                                elif isinstance(se_arg, Iterable):
                                    for n, element in enumerate(se_arg):
                                        element.id_short = f"{element.id_short}{n}"
                                        embedded_submodel_elements.append(element)
                                else:
                                    raise TypeError(
                                        f"Unknown type of value in submodel_element_args: {type(se_arg)}"
                                    )

                            super().__init__(
                                value=embedded_submodel_elements,
                                id_short=id_short,
                                type_value_list_element=type_value_list_element,
                                semantic_id_list_element=semantic_id_list_element,
                                value_type_list_element=value_type_list_element,
                                order_relevant=order_relevant,
                                display_name=display_name,
                                category=category,
                                description=description,
                                semantic_id=semantic_id,
                                qualifier=qualifier,
                                extension=extension,
                                supplemental_semantic_id=supplemental_semantic_id,
                                embedded_data_specifications=embedded_data_specifications,
                            )

                        def _check_constraints(self, new, existing) -> None:
                            # Since the id_short contains randomness, unset it temporarily for pretty and predictable error messages.
                            # This also prevents the random id_short from remaining set in case a constraint violation is encountered.
                            saved_id_short = new.id_short
                            new.id_short = None

                            # We relax constraint AASd-108here: It is allowed to add subclasses of the specified in type_value_list_element
                            if not isinstance(new, self.type_value_list_element):
                                raise base.AASConstraintViolation(
                                    108,
                                    "All first level elements must be of the type specified in "
                                    f"type_value_list_element={self.type_value_list_element.__name__}, "
                                    f"got {new!r}",
                                )

                            if (
                                self.semantic_id_list_element is not None
                                and new.semantic_id is not None
                                and new.semantic_id != self.semantic_id_list_element
                            ):
                                # Constraint AASd-115 specifies that if the semantic_id of an item is not specified
                                # but semantic_id_list_element is, the semantic_id of the new is assumed to be identical.
                                # Not really a constraint...
                                # TODO: maybe set the semantic_id of new to semantic_id_list_element if it is None
                                raise base.AASConstraintViolation(
                                    107,
                                    f"If semantic_id_list_element={self.semantic_id_list_element!r} "
                                    "is specified all first level children must have the same "
                                    f"semantic_id, got {new!r} with semantic_id={new.semantic_id!r}",
                                )

                            # If we got here we know that `new` is an instance of type_value_list_element and that type_value_list_element
                            # is either Property or Range. Thus, `new` must have the value_type property.
                            # Furthermore, value_type_list_element cannot be None, as this is already checked in __init__().
                            if (
                                isinstance(self.type_value_list_element, Property)
                                or isinstance(self.type_value_list_element, Range)
                                and not isinstance(
                                    new.value_type, self.value_type_list_element
                                )
                            ):  # type: ignore
                                raise base.AASConstraintViolation(
                                    109,
                                    "All first level elements must have the value_type "  # type: ignore
                                    "specified by value_type_list_element="
                                    f"{self.value_type_list_element.__name__}, got "  # type: ignore
                                    f"{new!r} with value_type={new.value_type.__name__}",
                                )  # type: ignore

                            # If semantic_id_list_element is not None that would already enforce the semantic_id for all first level
                            # elements. Thus, we only need to perform this check if semantic_id_list_element is None.
                            if (
                                new.semantic_id is not None
                                and self.semantic_id_list_element is None
                            ):
                                for item in existing:
                                    if (
                                        item.semantic_id is not None
                                        and new.semantic_id != item.semantic_id
                                    ):
                                        raise base.AASConstraintViolation(
                                            114,
                                            f"Element to be added {new!r} has semantic_id "
                                            f"{new.semantic_id!r}, while already contained element "
                                            f"{item!r} has semantic_id {item.semantic_id!r}, which "
                                            "aren't equal.",
                                        )

                            # Re-assign id_short
                            new.id_short = saved_id_short

                    class TranslationOfEntities(SubmodelElementList):
                        class Translationofentities_item(ReferenceElement):
                            def __init__(
                                self,
                                value: Reference,
                                id_short: Optional[str] = None,
                                display_name: Optional[
                                    MultiLanguageNameType
                                ] = MultiLanguageNameType(
                                    dict_={
                                        "en": "Translation of documents",
                                        "de": "Übersetzung von anderen Elementen",
                                    }
                                ),
                                category: Optional[str] = "PARAMETER",
                                description: Optional[MultiLanguageTextType] = None,
                                semantic_id: Optional[Reference] = ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="0173-1#02-ABK290#002",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                                qualifier: Iterable[Qualifier] = None,
                                extension: Iterable[Extension] = (),
                                supplemental_semantic_id: Iterable[Reference] = (),
                                embedded_data_specifications: Iterable[
                                    EmbeddedDataSpecification
                                ] = None,
                            ):
                                if qualifier is None:
                                    qualifier = (
                                        Qualifier(
                                            type_="SMT/Cardinality",
                                            value_type=str,
                                            value="OneToMany",
                                            value_id=None,
                                            kind=QualifierKind.CONCEPT_QUALIFIER,
                                            semantic_id=ExternalReference(
                                                key=(
                                                    Key(
                                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                                        value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                                    ),
                                                ),
                                                referred_semantic_id=None,
                                            ),
                                            supplemental_semantic_id=(),
                                        ),
                                        Qualifier(
                                            type_="AllowedIdShort",
                                            value_type=str,
                                            value="TranslationOf[\d{2,3}]",
                                            value_id=None,
                                            kind=QualifierKind.CONCEPT_QUALIFIER,
                                            semantic_id=ExternalReference(
                                                key=(
                                                    Key(
                                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                                        value="https://admin-shell.io/SubmodelTemplates/AllowedIdShort/1/0",
                                                    ),
                                                ),
                                                referred_semantic_id=None,
                                            ),
                                            supplemental_semantic_id=(),
                                        ),
                                    )

                                if embedded_data_specifications is None:
                                    embedded_data_specifications = []

                                super().__init__(
                                    value=value,
                                    id_short=id_short,
                                    display_name=display_name,
                                    category=category,
                                    description=description,
                                    semantic_id=semantic_id,
                                    qualifier=qualifier,
                                    extension=extension,
                                    supplemental_semantic_id=supplemental_semantic_id,
                                    embedded_data_specifications=embedded_data_specifications,
                                )

                        def __init__(
                            self,
                            translationofentities_items: Iterable[
                                Union[Reference, Translationofentities_item]
                            ],
                            id_short: Optional[str] = "TranslationOfEntities",
                            type_value_list_element: SubmodelElement = ReferenceElement,
                            semantic_id_list_element: Optional[Reference] = None,
                            value_type_list_element: Optional[DataTypeDefXsd] = None,
                            order_relevant: bool = True,
                            display_name: Optional[
                                MultiLanguageNameType
                            ] = MultiLanguageNameType(
                                dict_={
                                    "en": "Translation of other documents",
                                    "de": "Übersetzung von anderen Elementen",
                                }
                            ),
                            category: Optional[str] = None,
                            description: Optional[MultiLanguageTextType] = None,
                            semantic_id: Optional[Reference] = ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="0173-1#02-ABK290#002",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                            qualifier: Iterable[Qualifier] = None,
                            extension: Iterable[Extension] = (),
                            supplemental_semantic_id: Iterable[Reference] = (
                                ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="https://api.eclass-cdp.com/0173-1-02-ABK290-002",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                            ),
                            embedded_data_specifications: Iterable[
                                EmbeddedDataSpecification
                            ] = None,
                        ):
                            if qualifier is None:
                                qualifier = (
                                    Qualifier(
                                        type_="SMT/Cardinality",
                                        value_type=str,
                                        value="ZeroToOne",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/ExampleValue/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                )

                            if embedded_data_specifications is None:
                                embedded_data_specifications = []

                            # Build a list of submodel elements if a raw values were passed in the argument
                            if translationofentities_items and all(
                                [
                                    isinstance(i, Reference)
                                    for i in translationofentities_items
                                ]
                            ):
                                translationofentities_items = [
                                    self.Translationofentities_item(i)
                                    for i in translationofentities_items
                                ]

                            # Add all passed/initialized submodel elements to a single list
                            embedded_submodel_elements = []
                            for se_arg in [translationofentities_items]:
                                if se_arg is None:
                                    continue
                                elif isinstance(se_arg, SubmodelElement):
                                    embedded_submodel_elements.append(se_arg)
                                elif isinstance(se_arg, Iterable):
                                    for n, element in enumerate(se_arg):
                                        element.id_short = f"{element.id_short}{n}"
                                        embedded_submodel_elements.append(element)
                                else:
                                    raise TypeError(
                                        f"Unknown type of value in submodel_element_args: {type(se_arg)}"
                                    )

                            super().__init__(
                                value=embedded_submodel_elements,
                                id_short=id_short,
                                type_value_list_element=type_value_list_element,
                                semantic_id_list_element=semantic_id_list_element,
                                value_type_list_element=value_type_list_element,
                                order_relevant=order_relevant,
                                display_name=display_name,
                                category=category,
                                description=description,
                                semantic_id=semantic_id,
                                qualifier=qualifier,
                                extension=extension,
                                supplemental_semantic_id=supplemental_semantic_id,
                                embedded_data_specifications=embedded_data_specifications,
                            )

                        def _check_constraints(self, new, existing) -> None:
                            # Since the id_short contains randomness, unset it temporarily for pretty and predictable error messages.
                            # This also prevents the random id_short from remaining set in case a constraint violation is encountered.
                            saved_id_short = new.id_short
                            new.id_short = None

                            # We relax constraint AASd-108here: It is allowed to add subclasses of the specified in type_value_list_element
                            if not isinstance(new, self.type_value_list_element):
                                raise base.AASConstraintViolation(
                                    108,
                                    "All first level elements must be of the type specified in "
                                    f"type_value_list_element={self.type_value_list_element.__name__}, "
                                    f"got {new!r}",
                                )

                            if (
                                self.semantic_id_list_element is not None
                                and new.semantic_id is not None
                                and new.semantic_id != self.semantic_id_list_element
                            ):
                                # Constraint AASd-115 specifies that if the semantic_id of an item is not specified
                                # but semantic_id_list_element is, the semantic_id of the new is assumed to be identical.
                                # Not really a constraint...
                                # TODO: maybe set the semantic_id of new to semantic_id_list_element if it is None
                                raise base.AASConstraintViolation(
                                    107,
                                    f"If semantic_id_list_element={self.semantic_id_list_element!r} "
                                    "is specified all first level children must have the same "
                                    f"semantic_id, got {new!r} with semantic_id={new.semantic_id!r}",
                                )

                            # If we got here we know that `new` is an instance of type_value_list_element and that type_value_list_element
                            # is either Property or Range. Thus, `new` must have the value_type property.
                            # Furthermore, value_type_list_element cannot be None, as this is already checked in __init__().
                            if (
                                isinstance(self.type_value_list_element, Property)
                                or isinstance(self.type_value_list_element, Range)
                                and not isinstance(
                                    new.value_type, self.value_type_list_element
                                )
                            ):  # type: ignore
                                raise base.AASConstraintViolation(
                                    109,
                                    "All first level elements must have the value_type "  # type: ignore
                                    "specified by value_type_list_element="
                                    f"{self.value_type_list_element.__name__}, got "  # type: ignore
                                    f"{new!r} with value_type={new.value_type.__name__}",
                                )  # type: ignore

                            # If semantic_id_list_element is not None that would already enforce the semantic_id for all first level
                            # elements. Thus, we only need to perform this check if semantic_id_list_element is None.
                            if (
                                new.semantic_id is not None
                                and self.semantic_id_list_element is None
                            ):
                                for item in existing:
                                    if (
                                        item.semantic_id is not None
                                        and new.semantic_id != item.semantic_id
                                    ):
                                        raise base.AASConstraintViolation(
                                            114,
                                            f"Element to be added {new!r} has semantic_id "
                                            f"{new.semantic_id!r}, while already contained element "
                                            f"{item!r} has semantic_id {item.semantic_id!r}, which "
                                            "aren't equal.",
                                        )

                            # Re-assign id_short
                            new.id_short = saved_id_short

                    class DigitalFiles(SubmodelElementList):
                        class Digitalfiles_item(File):
                            def __init__(
                                self,
                                value: str,
                                id_short: Optional[str] = None,
                                content_type: str = "application/pdf",
                                display_name: Optional[
                                    MultiLanguageNameType
                                ] = MultiLanguageNameType(
                                    dict_={
                                        "en": "Name of the specific digital file@en",
                                        "de": "Name der spezifischen digitalen Datei@de",
                                    }
                                ),
                                category: Optional[str] = None,
                                description: Optional[MultiLanguageTextType] = None,
                                semantic_id: Optional[Reference] = ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="0173-1#02-ABK126#002",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                                qualifier: Iterable[Qualifier] = None,
                                extension: Iterable[Extension] = (),
                                supplemental_semantic_id: Iterable[Reference] = (),
                                embedded_data_specifications: Iterable[
                                    EmbeddedDataSpecification
                                ] = None,
                            ):
                                if qualifier is None:
                                    qualifier = (
                                        Qualifier(
                                            type_="SMT/Cardinality",
                                            value_type=str,
                                            value="OneToMany",
                                            value_id=None,
                                            kind=QualifierKind.CONCEPT_QUALIFIER,
                                            semantic_id=ExternalReference(
                                                key=(
                                                    Key(
                                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                                        value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                                    ),
                                                ),
                                                referred_semantic_id=None,
                                            ),
                                            supplemental_semantic_id=(),
                                        ),
                                        Qualifier(
                                            type_="ExampleValue",
                                            value_type=str,
                                            value="docu_cecc_fullmanual_DE.PDF",
                                            value_id=None,
                                            kind=QualifierKind.CONCEPT_QUALIFIER,
                                            semantic_id=ExternalReference(
                                                key=(
                                                    Key(
                                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                                        value="https://admin-shell.io/SubmodelTemplates/ExampleValue/1/0",
                                                    ),
                                                ),
                                                referred_semantic_id=None,
                                            ),
                                            supplemental_semantic_id=(),
                                        ),
                                        Qualifier(
                                            type_="AllowedIdShort",
                                            value_type=str,
                                            value="DigitalFile[\d{2,3}]",
                                            value_id=None,
                                            kind=QualifierKind.CONCEPT_QUALIFIER,
                                            semantic_id=ExternalReference(
                                                key=(
                                                    Key(
                                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                                        value="https://admin-shell.io/SubmodelTemplates/AllowedIdShort/1/0",
                                                    ),
                                                ),
                                                referred_semantic_id=None,
                                            ),
                                            supplemental_semantic_id=(),
                                        ),
                                    )

                                if embedded_data_specifications is None:
                                    embedded_data_specifications = []

                                super().__init__(
                                    value=value,
                                    id_short=id_short,
                                    content_type=content_type,
                                    display_name=display_name,
                                    category=category,
                                    description=description,
                                    semantic_id=semantic_id,
                                    qualifier=qualifier,
                                    extension=extension,
                                    supplemental_semantic_id=supplemental_semantic_id,
                                    embedded_data_specifications=embedded_data_specifications,
                                )

                        def __init__(
                            self,
                            digitalfiles_items: Iterable[Digitalfiles_item],
                            id_short: Optional[str] = "DigitalFiles",
                            type_value_list_element: SubmodelElement = File,
                            semantic_id_list_element: Optional[Reference] = None,
                            value_type_list_element: Optional[DataTypeDefXsd] = None,
                            order_relevant: bool = True,
                            display_name: Optional[
                                MultiLanguageNameType
                            ] = MultiLanguageNameType(
                                dict_={"en": "Digital files", "de": "Digitale Dateien"}
                            ),
                            category: Optional[str] = None,
                            description: Optional[MultiLanguageTextType] = None,
                            semantic_id: Optional[Reference] = ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="0173-1#02-ABK126#002",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                            qualifier: Iterable[Qualifier] = None,
                            extension: Iterable[Extension] = (),
                            supplemental_semantic_id: Iterable[Reference] = (
                                ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="https://api.eclass-cdp.com/0173-1-02-ABK126-002",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                            ),
                            embedded_data_specifications: Iterable[
                                EmbeddedDataSpecification
                            ] = None,
                        ):
                            if qualifier is None:
                                qualifier = (
                                    Qualifier(
                                        type_="SMT/Cardinality",
                                        value_type=str,
                                        value="One",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/ExampleValue/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                )

                            if embedded_data_specifications is None:
                                embedded_data_specifications = []

                            # Add all passed/initialized submodel elements to a single list
                            embedded_submodel_elements = []
                            for se_arg in [digitalfiles_items]:
                                if se_arg is None:
                                    continue
                                elif isinstance(se_arg, SubmodelElement):
                                    embedded_submodel_elements.append(se_arg)
                                elif isinstance(se_arg, Iterable):
                                    for n, element in enumerate(se_arg):
                                        element.id_short = f"{element.id_short}{n}"
                                        embedded_submodel_elements.append(element)
                                else:
                                    raise TypeError(
                                        f"Unknown type of value in submodel_element_args: {type(se_arg)}"
                                    )

                            super().__init__(
                                value=embedded_submodel_elements,
                                id_short=id_short,
                                type_value_list_element=type_value_list_element,
                                semantic_id_list_element=semantic_id_list_element,
                                value_type_list_element=value_type_list_element,
                                order_relevant=order_relevant,
                                display_name=display_name,
                                category=category,
                                description=description,
                                semantic_id=semantic_id,
                                qualifier=qualifier,
                                extension=extension,
                                supplemental_semantic_id=supplemental_semantic_id,
                                embedded_data_specifications=embedded_data_specifications,
                            )

                        def _check_constraints(self, new, existing) -> None:
                            # Since the id_short contains randomness, unset it temporarily for pretty and predictable error messages.
                            # This also prevents the random id_short from remaining set in case a constraint violation is encountered.
                            saved_id_short = new.id_short
                            new.id_short = None

                            # We relax constraint AASd-108here: It is allowed to add subclasses of the specified in type_value_list_element
                            if not isinstance(new, self.type_value_list_element):
                                raise base.AASConstraintViolation(
                                    108,
                                    "All first level elements must be of the type specified in "
                                    f"type_value_list_element={self.type_value_list_element.__name__}, "
                                    f"got {new!r}",
                                )

                            if (
                                self.semantic_id_list_element is not None
                                and new.semantic_id is not None
                                and new.semantic_id != self.semantic_id_list_element
                            ):
                                # Constraint AASd-115 specifies that if the semantic_id of an item is not specified
                                # but semantic_id_list_element is, the semantic_id of the new is assumed to be identical.
                                # Not really a constraint...
                                # TODO: maybe set the semantic_id of new to semantic_id_list_element if it is None
                                raise base.AASConstraintViolation(
                                    107,
                                    f"If semantic_id_list_element={self.semantic_id_list_element!r} "
                                    "is specified all first level children must have the same "
                                    f"semantic_id, got {new!r} with semantic_id={new.semantic_id!r}",
                                )

                            # If we got here we know that `new` is an instance of type_value_list_element and that type_value_list_element
                            # is either Property or Range. Thus, `new` must have the value_type property.
                            # Furthermore, value_type_list_element cannot be None, as this is already checked in __init__().
                            if (
                                isinstance(self.type_value_list_element, Property)
                                or isinstance(self.type_value_list_element, Range)
                                and not isinstance(
                                    new.value_type, self.value_type_list_element
                                )
                            ):  # type: ignore
                                raise base.AASConstraintViolation(
                                    109,
                                    "All first level elements must have the value_type "  # type: ignore
                                    "specified by value_type_list_element="
                                    f"{self.value_type_list_element.__name__}, got "  # type: ignore
                                    f"{new!r} with value_type={new.value_type.__name__}",
                                )  # type: ignore

                            # If semantic_id_list_element is not None that would already enforce the semantic_id for all first level
                            # elements. Thus, we only need to perform this check if semantic_id_list_element is None.
                            if (
                                new.semantic_id is not None
                                and self.semantic_id_list_element is None
                            ):
                                for item in existing:
                                    if (
                                        item.semantic_id is not None
                                        and new.semantic_id != item.semantic_id
                                    ):
                                        raise base.AASConstraintViolation(
                                            114,
                                            f"Element to be added {new!r} has semantic_id "
                                            f"{new.semantic_id!r}, while already contained element "
                                            f"{item!r} has semantic_id {item.semantic_id!r}, which "
                                            "aren't equal.",
                                        )

                            # Re-assign id_short
                            new.id_short = saved_id_short

                    class PreviewFile(File):
                        def __init__(
                            self,
                            value: str,
                            id_short: Optional[str] = "PreviewFile",
                            content_type: str = "image/jpeg",
                            display_name: Optional[
                                MultiLanguageNameType
                            ] = MultiLanguageNameType(
                                dict_={"en": "Preview file", "de": "Vorschaudatei"}
                            ),
                            category: Optional[str] = "PARAMETER",
                            description: Optional[MultiLanguageTextType] = None,
                            semantic_id: Optional[Reference] = ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="0173-1#02-ABK127#002",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                            qualifier: Iterable[Qualifier] = None,
                            extension: Iterable[Extension] = (),
                            supplemental_semantic_id: Iterable[Reference] = (
                                ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="https://api.eclass-cdp.com/0173-1-02-ABK127-002",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                            ),
                            embedded_data_specifications: Iterable[
                                EmbeddedDataSpecification
                            ] = None,
                        ):
                            if qualifier is None:
                                qualifier = (
                                    Qualifier(
                                        type_="SMT/Cardinality",
                                        value_type=str,
                                        value="ZeroToOne",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                    Qualifier(
                                        type_="ExampleValue",
                                        value_type=str,
                                        value="docu_cecc_fullmanual_DE.jpg",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/ExampleValue/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                    Qualifier(
                                        type_="AllowedIdShort",
                                        value_type=str,
                                        value="PreviewFile[\d{2,3}]",
                                        value_id=None,
                                        kind=QualifierKind.CONCEPT_QUALIFIER,
                                        semantic_id=ExternalReference(
                                            key=(
                                                Key(
                                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                                    value="https://admin-shell.io/SubmodelTemplates/AllowedIdShort/1/0",
                                                ),
                                            ),
                                            referred_semantic_id=None,
                                        ),
                                        supplemental_semantic_id=(),
                                    ),
                                )

                            if embedded_data_specifications is None:
                                embedded_data_specifications = []

                            super().__init__(
                                value=value,
                                id_short=id_short,
                                content_type=content_type,
                                display_name=display_name,
                                category=category,
                                description=description,
                                semantic_id=semantic_id,
                                qualifier=qualifier,
                                extension=extension,
                                supplemental_semantic_id=supplemental_semantic_id,
                                embedded_data_specifications=embedded_data_specifications,
                            )

                    def __init__(
                        self,
                        language: Union[Iterable[str], Language],
                        version: Union[str, Version],
                        title: Union[dict[str, str], MultiLanguageTextType, Title],
                        description_: Union[
                            dict[str, str], MultiLanguageTextType, Description
                        ],
                        statusSetDate: Union[Date, StatusSetDate],
                        statusValue: Union[str, StatusValue],
                        organizationShortName: Union[str, OrganizationShortName],
                        organizationOfficialName: Union[str, OrganizationOfficialName],
                        digitalFiles: DigitalFiles,
                        subtitle: Optional[
                            Union[dict[str, str], MultiLanguageTextType, Subtitle]
                        ] = None,
                        keyWords: Optional[
                            Union[dict[str, str], MultiLanguageTextType, KeyWords]
                        ] = None,
                        refersToEntities: Optional[RefersToEntities] = None,
                        basedOnReferences: Optional[BasedOnReferences] = None,
                        translationOfEntities: Optional[TranslationOfEntities] = None,
                        previewFile: Optional[PreviewFile] = None,
                        id_short: Optional[str] = None,
                        display_name: Optional[
                            MultiLanguageNameType
                        ] = MultiLanguageNameType(
                            dict_={"en": "Document version", "de": "Document version"}
                        ),
                        category: Optional[str] = None,
                        description: Optional[MultiLanguageTextType] = None,
                        semantic_id: Optional[Reference] = ExternalReference(
                            key=(
                                Key(
                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                    value="0173-1#02-ABI503#003/0173-1#01-AHF582#003",
                                ),
                            ),
                            referred_semantic_id=None,
                        ),
                        qualifier: Iterable[Qualifier] = None,
                        extension: Iterable[Extension] = (),
                        supplemental_semantic_id: Iterable[Reference] = (
                            ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="0173-1#02-ABI503#003~0/0173-1#01-AHF582#003",
                                    ),
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="https://api.eclass-cdp.com/0173-1-02-ABI503-003",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                        ),
                        embedded_data_specifications: Iterable[
                            EmbeddedDataSpecification
                        ] = None,
                    ):
                        if qualifier is None:
                            qualifier = (
                                Qualifier(
                                    type_="SMT/Cardinality",
                                    value_type=str,
                                    value="OneToMany",
                                    value_id=None,
                                    kind=QualifierKind.CONCEPT_QUALIFIER,
                                    semantic_id=ExternalReference(
                                        key=(
                                            Key(
                                                type_=KeyTypes.GLOBAL_REFERENCE,
                                                value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                            ),
                                        ),
                                        referred_semantic_id=None,
                                    ),
                                    supplemental_semantic_id=(),
                                ),
                            )

                        if embedded_data_specifications is None:
                            embedded_data_specifications = []

                        # Build a submodel element if a raw value was passed in the argument
                        if language and not isinstance(language, SubmodelElement):
                            language = self.Language(language)

                        # Build a submodel element if a raw value was passed in the argument
                        if version and not isinstance(version, SubmodelElement):
                            version = self.Version(version)

                        # Build a submodel element if a raw value was passed in the argument
                        if title and not isinstance(title, SubmodelElement):
                            title = self.Title(title)

                        # Build a submodel element if a raw value was passed in the argument
                        if subtitle and not isinstance(subtitle, SubmodelElement):
                            subtitle = self.Subtitle(subtitle)

                        # Build a submodel element if a raw value was passed in the argument
                        if description_ and not isinstance(
                            description_, SubmodelElement
                        ):
                            description_ = self.Description(description_)

                        # Build a submodel element if a raw value was passed in the argument
                        if keyWords and not isinstance(keyWords, SubmodelElement):
                            keyWords = self.KeyWords(keyWords)

                        # Build a submodel element if a raw value was passed in the argument
                        if statusSetDate and not isinstance(
                            statusSetDate, SubmodelElement
                        ):
                            statusSetDate = self.StatusSetDate(statusSetDate)

                        # Build a submodel element if a raw value was passed in the argument
                        if statusValue and not isinstance(statusValue, SubmodelElement):
                            statusValue = self.StatusValue(statusValue)

                        # Build a submodel element if a raw value was passed in the argument
                        if organizationShortName and not isinstance(
                            organizationShortName, SubmodelElement
                        ):
                            organizationShortName = self.OrganizationShortName(
                                organizationShortName
                            )

                        # Build a submodel element if a raw value was passed in the argument
                        if organizationOfficialName and not isinstance(
                            organizationOfficialName, SubmodelElement
                        ):
                            organizationOfficialName = self.OrganizationOfficialName(
                                organizationOfficialName
                            )

                        # Add all passed/initialized submodel elements to a single list
                        embedded_submodel_elements = []
                        for se_arg in [
                            language,
                            version,
                            title,
                            subtitle,
                            description_,
                            keyWords,
                            statusSetDate,
                            statusValue,
                            organizationShortName,
                            organizationOfficialName,
                            refersToEntities,
                            basedOnReferences,
                            translationOfEntities,
                            digitalFiles,
                            previewFile,
                        ]:
                            if se_arg is None:
                                continue
                            elif isinstance(se_arg, SubmodelElement):
                                embedded_submodel_elements.append(se_arg)
                            elif isinstance(se_arg, Iterable):
                                for n, element in enumerate(se_arg):
                                    element.id_short = f"{element.id_short}{n}"
                                    embedded_submodel_elements.append(element)
                            else:
                                raise TypeError(
                                    f"Unknown type of value in submodel_element_args: {type(se_arg)}"
                                )

                        super().__init__(
                            value=embedded_submodel_elements,
                            id_short=id_short,
                            display_name=display_name,
                            category=category,
                            description=description,
                            semantic_id=semantic_id,
                            qualifier=qualifier,
                            extension=extension,
                            supplemental_semantic_id=supplemental_semantic_id,
                            embedded_data_specifications=embedded_data_specifications,
                        )

                def __init__(
                    self,
                    documentversions_items: Iterable[Documentversions_item],
                    id_short: Optional[str] = "DocumentVersions",
                    type_value_list_element: SubmodelElement = SubmodelElementCollection,
                    semantic_id_list_element: Optional[Reference] = ExternalReference(
                        key=(
                            Key(
                                type_=KeyTypes.GLOBAL_REFERENCE,
                                value="0173-1#02-ABI503#003/0173-1#01-AHF582#003",
                            ),
                        ),
                        referred_semantic_id=None,
                    ),
                    value_type_list_element: Optional[DataTypeDefXsd] = None,
                    order_relevant: bool = True,
                    display_name: Optional[
                        MultiLanguageNameType
                    ] = MultiLanguageNameType(
                        dict_={"en": "Document versions", "de": "Dokumentenversionen"}
                    ),
                    category: Optional[str] = None,
                    description: Optional[MultiLanguageTextType] = None,
                    semantic_id: Optional[Reference] = ExternalReference(
                        key=(
                            Key(
                                type_=KeyTypes.GLOBAL_REFERENCE,
                                value="0173-1#02-ABI503#003",
                            ),
                        ),
                        referred_semantic_id=None,
                    ),
                    qualifier: Iterable[Qualifier] = None,
                    extension: Iterable[Extension] = (),
                    supplemental_semantic_id: Iterable[Reference] = (
                        ExternalReference(
                            key=(
                                Key(
                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                    value="https://api.eclass-cdp.com/0173-1-02-ABI503-003",
                                ),
                            ),
                            referred_semantic_id=None,
                        ),
                    ),
                    embedded_data_specifications: Iterable[
                        EmbeddedDataSpecification
                    ] = None,
                ):
                    if qualifier is None:
                        qualifier = (
                            Qualifier(
                                type_="SMT/Cardinality",
                                value_type=str,
                                value="One",
                                value_id=None,
                                kind=QualifierKind.CONCEPT_QUALIFIER,
                                semantic_id=ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                                supplemental_semantic_id=(),
                            ),
                        )

                    if embedded_data_specifications is None:
                        embedded_data_specifications = []

                    # Add all passed/initialized submodel elements to a single list
                    embedded_submodel_elements = []
                    for se_arg in [documentversions_items]:
                        if se_arg is None:
                            continue
                        elif isinstance(se_arg, SubmodelElement):
                            embedded_submodel_elements.append(se_arg)
                        elif isinstance(se_arg, Iterable):
                            for n, element in enumerate(se_arg):
                                element.id_short = f"{element.id_short}{n}"
                                embedded_submodel_elements.append(element)
                        else:
                            raise TypeError(
                                f"Unknown type of value in submodel_element_args: {type(se_arg)}"
                            )

                    super().__init__(
                        value=embedded_submodel_elements,
                        id_short=id_short,
                        type_value_list_element=type_value_list_element,
                        semantic_id_list_element=semantic_id_list_element,
                        value_type_list_element=value_type_list_element,
                        order_relevant=order_relevant,
                        display_name=display_name,
                        category=category,
                        description=description,
                        semantic_id=semantic_id,
                        qualifier=qualifier,
                        extension=extension,
                        supplemental_semantic_id=supplemental_semantic_id,
                        embedded_data_specifications=embedded_data_specifications,
                    )

                def _check_constraints(self, new, existing) -> None:
                    # Since the id_short contains randomness, unset it temporarily for pretty and predictable error messages.
                    # This also prevents the random id_short from remaining set in case a constraint violation is encountered.
                    saved_id_short = new.id_short
                    new.id_short = None

                    # We relax constraint AASd-108here: It is allowed to add subclasses of the specified in type_value_list_element
                    if not isinstance(new, self.type_value_list_element):
                        raise base.AASConstraintViolation(
                            108,
                            "All first level elements must be of the type specified in "
                            f"type_value_list_element={self.type_value_list_element.__name__}, "
                            f"got {new!r}",
                        )

                    if (
                        self.semantic_id_list_element is not None
                        and new.semantic_id is not None
                        and new.semantic_id != self.semantic_id_list_element
                    ):
                        # Constraint AASd-115 specifies that if the semantic_id of an item is not specified
                        # but semantic_id_list_element is, the semantic_id of the new is assumed to be identical.
                        # Not really a constraint...
                        # TODO: maybe set the semantic_id of new to semantic_id_list_element if it is None
                        raise base.AASConstraintViolation(
                            107,
                            f"If semantic_id_list_element={self.semantic_id_list_element!r} "
                            "is specified all first level children must have the same "
                            f"semantic_id, got {new!r} with semantic_id={new.semantic_id!r}",
                        )

                    # If we got here we know that `new` is an instance of type_value_list_element and that type_value_list_element
                    # is either Property or Range. Thus, `new` must have the value_type property.
                    # Furthermore, value_type_list_element cannot be None, as this is already checked in __init__().
                    if (
                        isinstance(self.type_value_list_element, Property)
                        or isinstance(self.type_value_list_element, Range)
                        and not isinstance(new.value_type, self.value_type_list_element)
                    ):  # type: ignore
                        raise base.AASConstraintViolation(
                            109,
                            "All first level elements must have the value_type "  # type: ignore
                            "specified by value_type_list_element="
                            f"{self.value_type_list_element.__name__}, got "  # type: ignore
                            f"{new!r} with value_type={new.value_type.__name__}",
                        )  # type: ignore

                    # If semantic_id_list_element is not None that would already enforce the semantic_id for all first level
                    # elements. Thus, we only need to perform this check if semantic_id_list_element is None.
                    if (
                        new.semantic_id is not None
                        and self.semantic_id_list_element is None
                    ):
                        for item in existing:
                            if (
                                item.semantic_id is not None
                                and new.semantic_id != item.semantic_id
                            ):
                                raise base.AASConstraintViolation(
                                    114,
                                    f"Element to be added {new!r} has semantic_id "
                                    f"{new.semantic_id!r}, while already contained element "
                                    f"{item!r} has semantic_id {item.semantic_id!r}, which "
                                    "aren't equal.",
                                )

                    # Re-assign id_short
                    new.id_short = saved_id_short

            class DocumentedEntities(SubmodelElementList):
                class Documentedentities_item(ReferenceElement):
                    def __init__(
                        self,
                        value: Reference,
                        id_short: Optional[str] = None,
                        display_name: Optional[MultiLanguageNameType] = None,
                        category: Optional[str] = "PARAMETER",
                        description: Optional[MultiLanguageTextType] = None,
                        semantic_id: Optional[Reference] = ExternalReference(
                            key=(
                                Key(
                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                    value="https://admin-shell.io/vdi/2770/1/0/Document/DocumentedEntity",
                                ),
                            ),
                            referred_semantic_id=None,
                        ),
                        qualifier: Iterable[Qualifier] = None,
                        extension: Iterable[Extension] = (),
                        supplemental_semantic_id: Iterable[Reference] = (),
                        embedded_data_specifications: Iterable[
                            EmbeddedDataSpecification
                        ] = None,
                    ):
                        if qualifier is None:
                            qualifier = (
                                Qualifier(
                                    type_="SMT/Cardinality",
                                    value_type=str,
                                    value="OneToMany",
                                    value_id=None,
                                    kind=QualifierKind.CONCEPT_QUALIFIER,
                                    semantic_id=ExternalReference(
                                        key=(
                                            Key(
                                                type_=KeyTypes.GLOBAL_REFERENCE,
                                                value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                            ),
                                        ),
                                        referred_semantic_id=None,
                                    ),
                                    supplemental_semantic_id=(),
                                ),
                            )

                        if embedded_data_specifications is None:
                            embedded_data_specifications = []

                        super().__init__(
                            value=value,
                            id_short=id_short,
                            display_name=display_name,
                            category=category,
                            description=description,
                            semantic_id=semantic_id,
                            qualifier=qualifier,
                            extension=extension,
                            supplemental_semantic_id=supplemental_semantic_id,
                            embedded_data_specifications=embedded_data_specifications,
                        )

                def __init__(
                    self,
                    documentedentities_items: Iterable[
                        Union[Reference, Documentedentities_item]
                    ],
                    id_short: Optional[str] = "DocumentedEntities",
                    type_value_list_element: SubmodelElement = ReferenceElement,
                    semantic_id_list_element: Optional[Reference] = None,
                    value_type_list_element: Optional[DataTypeDefXsd] = None,
                    order_relevant: bool = True,
                    display_name: Optional[MultiLanguageNameType] = None,
                    category: Optional[str] = None,
                    description: Optional[MultiLanguageTextType] = None,
                    semantic_id: Optional[Reference] = ExternalReference(
                        key=(
                            Key(
                                type_=KeyTypes.GLOBAL_REFERENCE,
                                value="https://admin-shell.io/vdi/2770/1/0/Document/DocumentedEntities",
                            ),
                        ),
                        referred_semantic_id=None,
                    ),
                    qualifier: Iterable[Qualifier] = None,
                    extension: Iterable[Extension] = (),
                    supplemental_semantic_id: Iterable[Reference] = (),
                    embedded_data_specifications: Iterable[
                        EmbeddedDataSpecification
                    ] = None,
                ):
                    if qualifier is None:
                        qualifier = (
                            Qualifier(
                                type_="SMT/Cardinality",
                                value_type=str,
                                value="ZeroToOne",
                                value_id=None,
                                kind=QualifierKind.CONCEPT_QUALIFIER,
                                semantic_id=ExternalReference(
                                    key=(
                                        Key(
                                            type_=KeyTypes.GLOBAL_REFERENCE,
                                            value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                        ),
                                    ),
                                    referred_semantic_id=None,
                                ),
                                supplemental_semantic_id=(),
                            ),
                        )

                    if embedded_data_specifications is None:
                        embedded_data_specifications = []

                    # Build a list of submodel elements if a raw values were passed in the argument
                    if documentedentities_items and all(
                        [isinstance(i, Reference) for i in documentedentities_items]
                    ):
                        documentedentities_items = [
                            self.Documentedentities_item(i)
                            for i in documentedentities_items
                        ]

                    # Add all passed/initialized submodel elements to a single list
                    embedded_submodel_elements = []
                    for se_arg in [documentedentities_items]:
                        if se_arg is None:
                            continue
                        elif isinstance(se_arg, SubmodelElement):
                            embedded_submodel_elements.append(se_arg)
                        elif isinstance(se_arg, Iterable):
                            for n, element in enumerate(se_arg):
                                element.id_short = f"{element.id_short}{n}"
                                embedded_submodel_elements.append(element)
                        else:
                            raise TypeError(
                                f"Unknown type of value in submodel_element_args: {type(se_arg)}"
                            )

                    super().__init__(
                        value=embedded_submodel_elements,
                        id_short=id_short,
                        type_value_list_element=type_value_list_element,
                        semantic_id_list_element=semantic_id_list_element,
                        value_type_list_element=value_type_list_element,
                        order_relevant=order_relevant,
                        display_name=display_name,
                        category=category,
                        description=description,
                        semantic_id=semantic_id,
                        qualifier=qualifier,
                        extension=extension,
                        supplemental_semantic_id=supplemental_semantic_id,
                        embedded_data_specifications=embedded_data_specifications,
                    )

                def _check_constraints(self, new, existing) -> None:
                    # Since the id_short contains randomness, unset it temporarily for pretty and predictable error messages.
                    # This also prevents the random id_short from remaining set in case a constraint violation is encountered.
                    saved_id_short = new.id_short
                    new.id_short = None

                    # We relax constraint AASd-108here: It is allowed to add subclasses of the specified in type_value_list_element
                    if not isinstance(new, self.type_value_list_element):
                        raise base.AASConstraintViolation(
                            108,
                            "All first level elements must be of the type specified in "
                            f"type_value_list_element={self.type_value_list_element.__name__}, "
                            f"got {new!r}",
                        )

                    if (
                        self.semantic_id_list_element is not None
                        and new.semantic_id is not None
                        and new.semantic_id != self.semantic_id_list_element
                    ):
                        # Constraint AASd-115 specifies that if the semantic_id of an item is not specified
                        # but semantic_id_list_element is, the semantic_id of the new is assumed to be identical.
                        # Not really a constraint...
                        # TODO: maybe set the semantic_id of new to semantic_id_list_element if it is None
                        raise base.AASConstraintViolation(
                            107,
                            f"If semantic_id_list_element={self.semantic_id_list_element!r} "
                            "is specified all first level children must have the same "
                            f"semantic_id, got {new!r} with semantic_id={new.semantic_id!r}",
                        )

                    # If we got here we know that `new` is an instance of type_value_list_element and that type_value_list_element
                    # is either Property or Range. Thus, `new` must have the value_type property.
                    # Furthermore, value_type_list_element cannot be None, as this is already checked in __init__().
                    if (
                        isinstance(self.type_value_list_element, Property)
                        or isinstance(self.type_value_list_element, Range)
                        and not isinstance(new.value_type, self.value_type_list_element)
                    ):  # type: ignore
                        raise base.AASConstraintViolation(
                            109,
                            "All first level elements must have the value_type "  # type: ignore
                            "specified by value_type_list_element="
                            f"{self.value_type_list_element.__name__}, got "  # type: ignore
                            f"{new!r} with value_type={new.value_type.__name__}",
                        )  # type: ignore

                    # If semantic_id_list_element is not None that would already enforce the semantic_id for all first level
                    # elements. Thus, we only need to perform this check if semantic_id_list_element is None.
                    if (
                        new.semantic_id is not None
                        and self.semantic_id_list_element is None
                    ):
                        for item in existing:
                            if (
                                item.semantic_id is not None
                                and new.semantic_id != item.semantic_id
                            ):
                                raise base.AASConstraintViolation(
                                    114,
                                    f"Element to be added {new!r} has semantic_id "
                                    f"{new.semantic_id!r}, while already contained element "
                                    f"{item!r} has semantic_id {item.semantic_id!r}, which "
                                    "aren't equal.",
                                )

                    # Re-assign id_short
                    new.id_short = saved_id_short

            def __init__(
                self,
                documentIds: DocumentIds,
                documentClassifications: DocumentClassifications,
                documentVersions: DocumentVersions,
                documentedEntities: Optional[DocumentedEntities] = None,
                id_short: Optional[str] = None,
                display_name: Optional[MultiLanguageNameType] = None,
                category: Optional[str] = None,
                description: Optional[MultiLanguageTextType] = MultiLanguageTextType(
                    dict_={
                        "en": "This SubmodelElementCollection holds the information for a VDI 2770 Document entity"
                    }
                ),
                semantic_id: Optional[Reference] = ExternalReference(
                    key=(
                        Key(
                            type_=KeyTypes.GLOBAL_REFERENCE,
                            value="0173-1#02-ABI500#003/0173-1#01-AHF579#003",
                        ),
                    ),
                    referred_semantic_id=None,
                ),
                qualifier: Iterable[Qualifier] = None,
                extension: Iterable[Extension] = (),
                supplemental_semantic_id: Iterable[Reference] = (
                    ExternalReference(
                        key=(
                            Key(
                                type_=KeyTypes.GLOBAL_REFERENCE,
                                value="0173-1#02-ABI500#003~0/0173-1#01-AHF579#003",
                            ),
                            Key(
                                type_=KeyTypes.GLOBAL_REFERENCE,
                                value="https://api.eclass-cdp.com/0173-1-02-ABI500-003/0173-1-01-AHF579-003",
                            ),
                        ),
                        referred_semantic_id=None,
                    ),
                ),
                embedded_data_specifications: Iterable[
                    EmbeddedDataSpecification
                ] = None,
            ):
                if qualifier is None:
                    qualifier = (
                        Qualifier(
                            type_="SMT/Cardinality",
                            value_type=str,
                            value="OneToMany",
                            value_id=None,
                            kind=QualifierKind.CONCEPT_QUALIFIER,
                            semantic_id=ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                            supplemental_semantic_id=(),
                        ),
                    )

                if embedded_data_specifications is None:
                    embedded_data_specifications = []

                # Add all passed/initialized submodel elements to a single list
                embedded_submodel_elements = []
                for se_arg in [
                    documentIds,
                    documentClassifications,
                    documentVersions,
                    documentedEntities,
                ]:
                    if se_arg is None:
                        continue
                    elif isinstance(se_arg, SubmodelElement):
                        embedded_submodel_elements.append(se_arg)
                    elif isinstance(se_arg, Iterable):
                        for n, element in enumerate(se_arg):
                            element.id_short = f"{element.id_short}{n}"
                            embedded_submodel_elements.append(element)
                    else:
                        raise TypeError(
                            f"Unknown type of value in submodel_element_args: {type(se_arg)}"
                        )

                super().__init__(
                    value=embedded_submodel_elements,
                    id_short=id_short,
                    display_name=display_name,
                    category=category,
                    description=description,
                    semantic_id=semantic_id,
                    qualifier=qualifier,
                    extension=extension,
                    supplemental_semantic_id=supplemental_semantic_id,
                    embedded_data_specifications=embedded_data_specifications,
                )

        def __init__(
            self,
            documents_items: Iterable[Documents_item],
            id_short: Optional[str] = "Documents",
            type_value_list_element: SubmodelElement = SubmodelElementCollection,
            semantic_id_list_element: Optional[Reference] = ExternalReference(
                key=(
                    Key(
                        type_=KeyTypes.GLOBAL_REFERENCE,
                        value="0173-1#02-ABI500#003/0173-1#01-AHF579#003",
                    ),
                ),
                referred_semantic_id=None,
            ),
            value_type_list_element: Optional[DataTypeDefXsd] = None,
            order_relevant: bool = True,
            display_name: Optional[MultiLanguageNameType] = MultiLanguageNameType(
                dict_={
                    "en": "Documents (handover documentation)",
                    "de": "Dokumente (Übergabedokumentation)",
                }
            ),
            category: Optional[str] = None,
            description: Optional[MultiLanguageTextType] = None,
            semantic_id: Optional[Reference] = ExternalReference(
                key=(
                    Key(type_=KeyTypes.GLOBAL_REFERENCE, value="0173-1#02-ABI500#003"),
                ),
                referred_semantic_id=None,
            ),
            qualifier: Iterable[Qualifier] = None,
            extension: Iterable[Extension] = (),
            supplemental_semantic_id: Iterable[Reference] = (
                ExternalReference(
                    key=(
                        Key(
                            type_=KeyTypes.GLOBAL_REFERENCE,
                            value="https://api.eclass-cdp.com/0173-1-02-ABI500-003",
                        ),
                    ),
                    referred_semantic_id=None,
                ),
            ),
            embedded_data_specifications: Iterable[EmbeddedDataSpecification] = None,
        ):
            if qualifier is None:
                qualifier = (
                    Qualifier(
                        type_="SMT/Cardinality",
                        value_type=str,
                        value="One",
                        value_id=None,
                        kind=QualifierKind.CONCEPT_QUALIFIER,
                        semantic_id=ExternalReference(
                            key=(
                                Key(
                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                    value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                ),
                            ),
                            referred_semantic_id=None,
                        ),
                        supplemental_semantic_id=(),
                    ),
                )

            if embedded_data_specifications is None:
                embedded_data_specifications = []

            # Add all passed/initialized submodel elements to a single list
            embedded_submodel_elements = []
            for se_arg in [documents_items]:
                if se_arg is None:
                    continue
                elif isinstance(se_arg, SubmodelElement):
                    embedded_submodel_elements.append(se_arg)
                elif isinstance(se_arg, Iterable):
                    for n, element in enumerate(se_arg):
                        element.id_short = f"{element.id_short}{n}"
                        embedded_submodel_elements.append(element)
                else:
                    raise TypeError(
                        f"Unknown type of value in submodel_element_args: {type(se_arg)}"
                    )

            super().__init__(
                value=embedded_submodel_elements,
                id_short=id_short,
                type_value_list_element=type_value_list_element,
                semantic_id_list_element=semantic_id_list_element,
                value_type_list_element=value_type_list_element,
                order_relevant=order_relevant,
                display_name=display_name,
                category=category,
                description=description,
                semantic_id=semantic_id,
                qualifier=qualifier,
                extension=extension,
                supplemental_semantic_id=supplemental_semantic_id,
                embedded_data_specifications=embedded_data_specifications,
            )

        def _check_constraints(self, new, existing) -> None:
            # Since the id_short contains randomness, unset it temporarily for pretty and predictable error messages.
            # This also prevents the random id_short from remaining set in case a constraint violation is encountered.
            saved_id_short = new.id_short
            new.id_short = None

            # We relax constraint AASd-108here: It is allowed to add subclasses of the specified in type_value_list_element
            if not isinstance(new, self.type_value_list_element):
                raise base.AASConstraintViolation(
                    108,
                    "All first level elements must be of the type specified in "
                    f"type_value_list_element={self.type_value_list_element.__name__}, "
                    f"got {new!r}",
                )

            if (
                self.semantic_id_list_element is not None
                and new.semantic_id is not None
                and new.semantic_id != self.semantic_id_list_element
            ):
                # Constraint AASd-115 specifies that if the semantic_id of an item is not specified
                # but semantic_id_list_element is, the semantic_id of the new is assumed to be identical.
                # Not really a constraint...
                # TODO: maybe set the semantic_id of new to semantic_id_list_element if it is None
                raise base.AASConstraintViolation(
                    107,
                    f"If semantic_id_list_element={self.semantic_id_list_element!r} "
                    "is specified all first level children must have the same "
                    f"semantic_id, got {new!r} with semantic_id={new.semantic_id!r}",
                )

            # If we got here we know that `new` is an instance of type_value_list_element and that type_value_list_element
            # is either Property or Range. Thus, `new` must have the value_type property.
            # Furthermore, value_type_list_element cannot be None, as this is already checked in __init__().
            if (
                isinstance(self.type_value_list_element, Property)
                or isinstance(self.type_value_list_element, Range)
                and not isinstance(new.value_type, self.value_type_list_element)
            ):  # type: ignore
                raise base.AASConstraintViolation(
                    109,
                    "All first level elements must have the value_type "  # type: ignore
                    "specified by value_type_list_element="
                    f"{self.value_type_list_element.__name__}, got "  # type: ignore
                    f"{new!r} with value_type={new.value_type.__name__}",
                )  # type: ignore

            # If semantic_id_list_element is not None that would already enforce the semantic_id for all first level
            # elements. Thus, we only need to perform this check if semantic_id_list_element is None.
            if new.semantic_id is not None and self.semantic_id_list_element is None:
                for item in existing:
                    if (
                        item.semantic_id is not None
                        and new.semantic_id != item.semantic_id
                    ):
                        raise base.AASConstraintViolation(
                            114,
                            f"Element to be added {new!r} has semantic_id "
                            f"{new.semantic_id!r}, while already contained element "
                            f"{item!r} has semantic_id {item.semantic_id!r}, which "
                            "aren't equal.",
                        )

            # Re-assign id_short
            new.id_short = saved_id_short

    class Entities(SubmodelElementList):
        class Entities_item(Entity):
            def __init__(
                self,
                id_short: Optional[str] = None,
                entity_type: EntityType = EntityType.CO_MANAGED_ENTITY,
                statement: Iterable[SubmodelElement] = (),
                global_asset_id: Optional[str] = None,
                specific_asset_id: Iterable[SpecificAssetId] = (),
                display_name: Optional[MultiLanguageNameType] = None,
                category: Optional[str] = "PARAMETER",
                description: Optional[MultiLanguageTextType] = None,
                semantic_id: Optional[Reference] = ExternalReference(
                    key=(
                        Key(
                            type_=KeyTypes.GLOBAL_REFERENCE,
                            value="https://admin-shell.io/vdi/2770/1/0/EntityForDocumentation",
                        ),
                    ),
                    referred_semantic_id=None,
                ),
                qualifier: Iterable[Qualifier] = None,
                extension: Iterable[Extension] = (),
                supplemental_semantic_id: Iterable[Reference] = (),
                embedded_data_specifications: Iterable[
                    EmbeddedDataSpecification
                ] = None,
            ):
                if qualifier is None:
                    qualifier = (
                        Qualifier(
                            type_="SMT/Cardinality",
                            value_type=str,
                            value="OneToMany",
                            value_id=None,
                            kind=QualifierKind.CONCEPT_QUALIFIER,
                            semantic_id=ExternalReference(
                                key=(
                                    Key(
                                        type_=KeyTypes.GLOBAL_REFERENCE,
                                        value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                    ),
                                ),
                                referred_semantic_id=None,
                            ),
                            supplemental_semantic_id=(),
                        ),
                    )

                if embedded_data_specifications is None:
                    embedded_data_specifications = []

                super().__init__(
                    id_short=id_short,
                    entity_type=entity_type,
                    statement=statement,
                    global_asset_id=global_asset_id,
                    specific_asset_id=specific_asset_id,
                    display_name=display_name,
                    category=category,
                    description=description,
                    semantic_id=semantic_id,
                    qualifier=qualifier,
                    extension=extension,
                    supplemental_semantic_id=supplemental_semantic_id,
                    embedded_data_specifications=embedded_data_specifications,
                )

        def __init__(
            self,
            entities_items: Iterable[Entities_item],
            id_short: Optional[str] = "Entities",
            type_value_list_element: SubmodelElement = Entity,
            semantic_id_list_element: Optional[Reference] = None,
            value_type_list_element: Optional[DataTypeDefXsd] = None,
            order_relevant: bool = True,
            display_name: Optional[MultiLanguageNameType] = None,
            category: Optional[str] = None,
            description: Optional[MultiLanguageTextType] = None,
            semantic_id: Optional[Reference] = ExternalReference(
                key=(
                    Key(
                        type_=KeyTypes.GLOBAL_REFERENCE,
                        value="https://admin-shell.io/vdi/2770/1/0/EntitiesForDocumentation",
                    ),
                ),
                referred_semantic_id=None,
            ),
            qualifier: Iterable[Qualifier] = None,
            extension: Iterable[Extension] = (),
            supplemental_semantic_id: Iterable[Reference] = (),
            embedded_data_specifications: Iterable[EmbeddedDataSpecification] = None,
        ):
            if qualifier is None:
                qualifier = (
                    Qualifier(
                        type_="SMT/Cardinality",
                        value_type=str,
                        value="ZeroToOne",
                        value_id=None,
                        kind=QualifierKind.CONCEPT_QUALIFIER,
                        semantic_id=ExternalReference(
                            key=(
                                Key(
                                    type_=KeyTypes.GLOBAL_REFERENCE,
                                    value="https://admin-shell.io/SubmodelTemplates/Cardinality/1/0",
                                ),
                            ),
                            referred_semantic_id=None,
                        ),
                        supplemental_semantic_id=(),
                    ),
                )

            if embedded_data_specifications is None:
                embedded_data_specifications = []

            # Add all passed/initialized submodel elements to a single list
            embedded_submodel_elements = []
            for se_arg in [entities_items]:
                if se_arg is None:
                    continue
                elif isinstance(se_arg, SubmodelElement):
                    embedded_submodel_elements.append(se_arg)
                elif isinstance(se_arg, Iterable):
                    for n, element in enumerate(se_arg):
                        element.id_short = f"{element.id_short}{n}"
                        embedded_submodel_elements.append(element)
                else:
                    raise TypeError(
                        f"Unknown type of value in submodel_element_args: {type(se_arg)}"
                    )

            super().__init__(
                value=embedded_submodel_elements,
                id_short=id_short,
                type_value_list_element=type_value_list_element,
                semantic_id_list_element=semantic_id_list_element,
                value_type_list_element=value_type_list_element,
                order_relevant=order_relevant,
                display_name=display_name,
                category=category,
                description=description,
                semantic_id=semantic_id,
                qualifier=qualifier,
                extension=extension,
                supplemental_semantic_id=supplemental_semantic_id,
                embedded_data_specifications=embedded_data_specifications,
            )

        def _check_constraints(self, new, existing) -> None:
            # Since the id_short contains randomness, unset it temporarily for pretty and predictable error messages.
            # This also prevents the random id_short from remaining set in case a constraint violation is encountered.
            saved_id_short = new.id_short
            new.id_short = None

            # We relax constraint AASd-108here: It is allowed to add subclasses of the specified in type_value_list_element
            if not isinstance(new, self.type_value_list_element):
                raise base.AASConstraintViolation(
                    108,
                    "All first level elements must be of the type specified in "
                    f"type_value_list_element={self.type_value_list_element.__name__}, "
                    f"got {new!r}",
                )

            if (
                self.semantic_id_list_element is not None
                and new.semantic_id is not None
                and new.semantic_id != self.semantic_id_list_element
            ):
                # Constraint AASd-115 specifies that if the semantic_id of an item is not specified
                # but semantic_id_list_element is, the semantic_id of the new is assumed to be identical.
                # Not really a constraint...
                # TODO: maybe set the semantic_id of new to semantic_id_list_element if it is None
                raise base.AASConstraintViolation(
                    107,
                    f"If semantic_id_list_element={self.semantic_id_list_element!r} "
                    "is specified all first level children must have the same "
                    f"semantic_id, got {new!r} with semantic_id={new.semantic_id!r}",
                )

            # If we got here we know that `new` is an instance of type_value_list_element and that type_value_list_element
            # is either Property or Range. Thus, `new` must have the value_type property.
            # Furthermore, value_type_list_element cannot be None, as this is already checked in __init__().
            if (
                isinstance(self.type_value_list_element, Property)
                or isinstance(self.type_value_list_element, Range)
                and not isinstance(new.value_type, self.value_type_list_element)
            ):  # type: ignore
                raise base.AASConstraintViolation(
                    109,
                    "All first level elements must have the value_type "  # type: ignore
                    "specified by value_type_list_element="
                    f"{self.value_type_list_element.__name__}, got "  # type: ignore
                    f"{new!r} with value_type={new.value_type.__name__}",
                )  # type: ignore

            # If semantic_id_list_element is not None that would already enforce the semantic_id for all first level
            # elements. Thus, we only need to perform this check if semantic_id_list_element is None.
            if new.semantic_id is not None and self.semantic_id_list_element is None:
                for item in existing:
                    if (
                        item.semantic_id is not None
                        and new.semantic_id != item.semantic_id
                    ):
                        raise base.AASConstraintViolation(
                            114,
                            f"Element to be added {new!r} has semantic_id "
                            f"{new.semantic_id!r}, while already contained element "
                            f"{item!r} has semantic_id {item.semantic_id!r}, which "
                            "aren't equal.",
                        )

            # Re-assign id_short
            new.id_short = saved_id_short

    def __init__(
        self,
        id_: str,
        documents: Documents,
        entities: Optional[Entities] = None,
        id_short: Optional[str] = "HandoverDocumentation",
        display_name: Optional[MultiLanguageNameType] = None,
        category: Optional[str] = None,
        description: Optional[MultiLanguageTextType] = MultiLanguageTextType(
            dict_={
                "en": "The Submodel defines a set meta data for the handover of documentation from the manufacturer to the operator for industrial equipment"
            }
        ),
        administration: Optional[AdministrativeInformation] = AdministrativeInformation(
            version="2",
            revision="0",
            creator=None,
            template_id="https://admin-shell.io/idta-02004-2-0",
            embedded_data_specifications=[],
        ),
        semantic_id: Optional[Reference] = ModelReference(
            key=(Key(type_=KeyTypes.SUBMODEL, value="0173-1#01-AHF578#003"),),
            type_=Submodel,
            referred_semantic_id=None,
        ),
        qualifier: Iterable[Qualifier] = None,
        kind: ModellingKind = ModellingKind.TEMPLATE,
        extension: Iterable[Extension] = (),
        supplemental_semantic_id: Iterable[Reference] = (
            ExternalReference(
                key=(
                    Key(
                        type_=KeyTypes.GLOBAL_REFERENCE,
                        value="https://api.eclass-cdp.com/0173-1-01-AHF578-003",
                    ),
                ),
                referred_semantic_id=None,
            ),
        ),
        embedded_data_specifications: Iterable[EmbeddedDataSpecification] = None,
    ):
        if qualifier is None:
            qualifier = ()

        if embedded_data_specifications is None:
            embedded_data_specifications = []

        # Add all passed/initialized submodel elements to a single list
        embedded_submodel_elements = []
        for se_arg in [documents, entities]:
            if se_arg is None:
                continue
            elif isinstance(se_arg, SubmodelElement):
                embedded_submodel_elements.append(se_arg)
            elif isinstance(se_arg, Iterable):
                for n, element in enumerate(se_arg):
                    element.id_short = f"{element.id_short}{n}"
                    embedded_submodel_elements.append(element)
            else:
                raise TypeError(
                    f"Unknown type of value in submodel_element_args: {type(se_arg)}"
                )

        super().__init__(
            submodel_element=embedded_submodel_elements,
            id_=id_,
            id_short=id_short,
            display_name=display_name,
            category=category,
            description=description,
            administration=administration,
            semantic_id=semantic_id,
            qualifier=qualifier,
            kind=kind,
            extension=extension,
            supplemental_semantic_id=supplemental_semantic_id,
            embedded_data_specifications=embedded_data_specifications,
        )
