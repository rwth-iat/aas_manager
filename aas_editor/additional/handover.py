from typing import *
import inspect
from basyx.aas.model import *
from basyx.aas.model.datatypes import *


class HandoverDocumentation(Submodel):
  class NumberOfDocuments(Property):
    def __init__(
      self,
      value: int,
      id_short: Optional[str] = "numberOfDocuments",
      value_type: DataTypeDefXsd = int,
      value_id: Optional[Reference] = None,
      display_name: Optional[MultiLanguageNameType] = None,
      category: Optional[str] = "PARAMETER",
      description: Optional[MultiLanguageTextType] = None,
      semantic_id: Optional[Reference] = ExternalReference(
        key=(
            Key(type_=KeyTypes.GLOBAL_REFERENCE, value="0173-1#02-ABH990#001"),
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
            type_="Relevance",
            value_type=str,
            value="optional",
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

  class Document(SubmodelElementCollection):
    class DocumentId(SubmodelElementCollection):
      class DocumentDomainId(Property):
        def __init__(
          self,
          value: str,
          id_short: Optional[str] = "DocumentDomainId",
          value_type: DataTypeDefXsd = str,
          value_id: Optional[Reference] = None,
          display_name: Optional[MultiLanguageNameType] = None,
          category: Optional[str] = "PARAMETER",
          description: Optional[
            MultiLanguageTextType
          ] = MultiLanguageTextType(
            dict_={
              "en": "Identification of the domain in which the given DocumentId is unique. The domain ID can e.g., be the name or acronym of the providing organisation."
            }
          ),
          semantic_id: Optional[Reference] = ExternalReference(
            key=(
                Key(
                  type_=KeyTypes.GLOBAL_REFERENCE,
                  value="0173-1#02-ABH994#001",
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
                type_="Cardinality",
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
                value="1213455566",
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

      class ValueId(Property):
        def __init__(
          self,
          value: str,
          id_short: Optional[str] = "ValueId",
          value_type: DataTypeDefXsd = str,
          value_id: Optional[Reference] = None,
          display_name: Optional[MultiLanguageNameType] = None,
          category: Optional[str] = "PARAMETER",
          description: Optional[
            MultiLanguageTextType
          ] = MultiLanguageTextType(
            dict_={
              "en": "Identification number of the Document within a given domain, e.g. the providing organisation."
            }
          ),
          semantic_id: Optional[Reference] = ExternalReference(
            key=(
                Key(
                  type_=KeyTypes.GLOBAL_REFERENCE,
                  value="0173-1#02-AAO099#002",
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
                type_="Cardinality",
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

      class IsPrimary(Property):
        def __init__(
          self,
          value: bool,
          id_short: Optional[str] = "IsPrimary",
          value_type: DataTypeDefXsd = bool,
          value_id: Optional[Reference] = None,
          display_name: Optional[MultiLanguageNameType] = None,
          category: Optional[str] = "PARAMETER",
          description: Optional[
            MultiLanguageTextType
          ] = MultiLanguageTextType(
            dict_={
              "en": "Flag indicating that a DocumentId within a collection of at least two DocumentId`s is the ‘primary’ identifier for the document. This is the preferred ID of the document (commonly from the point of view of the owner of the asset). Note: can be omitted, if the ID is not primary. Note: can be omitted, if only one ID is for a Document. Contraint: only one DocumentId in a collection may be marked as primary."
            }
          ),
          semantic_id: Optional[Reference] = ExternalReference(
            key=(
                Key(
                  type_=KeyTypes.GLOBAL_REFERENCE,
                  value="0173-1#02-ABH995#001",
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
                type_="Cardinality",
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
        valueId: Union[str, ValueId],
        isPrimary: Optional[Union[bool, IsPrimary]] = None,
        id_short: Optional[str] = "DocumentId",
        display_name: Optional[MultiLanguageNameType] = None,
        category: Optional[str] = "PARAMETER",
        description: Optional[MultiLanguageTextType] = MultiLanguageTextType(
          dict_={
            "en": "Set of document identifiers for the Document. One ID in this collection should be used as a preferred ID"
          }
        ),
        semantic_id: Optional[Reference] = ExternalReference(
          key=(
              Key(
                type_=KeyTypes.GLOBAL_REFERENCE,
                value="0173-1#02-ABI501#001/0173-1#01-AHF580#001*01",
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
              type_="Cardinality",
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
        if valueId and not isinstance(valueId, SubmodelElement):
          valueId = self.ValueId(valueId)

        # Build a submodel element if a raw value was passed in the argument
        if isPrimary and not isinstance(isPrimary, SubmodelElement):
          isPrimary = self.IsPrimary(isPrimary)

        # Add all passed/initialized submodel elements to a single list
        embedded_submodel_elements = []
        for se_arg in [documentDomainId, valueId, isPrimary]:
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

    class DocumentClassification(SubmodelElementCollection):
      class ClassId(Property):
        def __init__(
          self,
          value: str,
          id_short: Optional[str] = "ClassId",
          value_type: DataTypeDefXsd = str,
          value_id: Optional[Reference] = None,
          display_name: Optional[MultiLanguageNameType] = None,
          category: Optional[str] = "PARAMETER",
          description: Optional[
            MultiLanguageTextType
          ] = MultiLanguageTextType(
            dict_={
              "en": "Unique ID of the document class within a ClassficationSystem. Constraint: If ClassificationSystem is set to “VDI2770:2018”, the given IDs of VDI2770:2018 shall be used"
            }
          ),
          semantic_id: Optional[Reference] = ExternalReference(
            key=(
                Key(
                  type_=KeyTypes.GLOBAL_REFERENCE,
                  value="0173-1#02-ABH996#001",
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
                type_="Cardinality",
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
          value: LangStringSet,
          id_short: Optional[str] = "ClassName",
          value_id: Optional[Reference] = None,
          display_name: Optional[MultiLanguageNameType] = None,
          category: Optional[str] = "PARAMETER",
          description: Optional[
            MultiLanguageTextType
          ] = MultiLanguageTextType(
            dict_={
              "en": "List of language-dependent names of the selected ClassID. Constraint: If ClassificationSystem is set to “VDI2770:2018” then the given names of VDI2770:2018 need be used. Constraint: languages shall match at least the language specifications of the included DocumentVersions (below)."
            }
          ),
          semantic_id: Optional[Reference] = ExternalReference(
            key=(
                Key(
                  type_=KeyTypes.GLOBAL_REFERENCE,
                  value="0173-1#02-AAO102#003",
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
                type_="Cardinality",
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
          display_name: Optional[MultiLanguageNameType] = None,
          category: Optional[str] = "PARAMETER",
          description: Optional[
            MultiLanguageTextType
          ] = MultiLanguageTextType(
            dict_={
              "en": 'Identification of the classification system. For classifications according VDI 2270 always set to "VDI2770:2018". Further classification systems are commonly used, such as "IEC61355-1:2008".'
            }
          ),
          semantic_id: Optional[Reference] = ExternalReference(
            key=(
                Key(
                  type_=KeyTypes.GLOBAL_REFERENCE,
                  value="0173-1#02-ABH997#001",
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
                type_="Cardinality",
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
        className: Union[LangStringSet, ClassName],
        classificationSystem: Union[str, ClassificationSystem],
        id_short: Optional[str] = "DocumentClassification",
        display_name: Optional[MultiLanguageNameType] = None,
        category: Optional[str] = "PARAMETER",
        description: Optional[MultiLanguageTextType] = MultiLanguageTextType(
          dict_={
            "en": "Set of information for describing the classification of the Document according to ClassificationSystems. Constraint: at least one classification according to VDI 2770 shall be provided."
          }
        ),
        semantic_id: Optional[Reference] = ExternalReference(
          key=(
              Key(
                type_=KeyTypes.GLOBAL_REFERENCE,
                value="0173-1#02-ABI502#001/0173-1#01-AHF581#001*01",
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
              type_="Cardinality",
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

    class DocumentVersion(SubmodelElementCollection):
      class Language(Property):
        def __init__(
          self,
          value: str,
          id_short: Optional[str] = "Language",
          value_type: DataTypeDefXsd = str,
          value_id: Optional[Reference] = None,
          display_name: Optional[MultiLanguageNameType] = None,
          category: Optional[str] = "PARAMETER",
          description: Optional[
            MultiLanguageTextType
          ] = MultiLanguageTextType(
            dict_={
              "en": "This property contains a list of languages used within the DocumentVersion. Each property codes one language identification according to ISO 639-1 or ISO 639-2 used in the Document."
            }
          ),
          semantic_id: Optional[Reference] = ExternalReference(
            key=(
                Key(
                  type_=KeyTypes.GLOBAL_REFERENCE,
                  value="0173-1#02-AAN468#006",
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
                type_="Cardinality",
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
              Qualifier(
                type_="AllowedIdShort",
                value_type=str,
                value="Language[\d{2,3}]",
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

      class DocumentVersionId(Property):
        def __init__(
          self,
          value: str,
          id_short: Optional[str] = "DocumentVersionId",
          value_type: DataTypeDefXsd = str,
          value_id: Optional[Reference] = None,
          display_name: Optional[MultiLanguageNameType] = None,
          category: Optional[str] = "PARAMETER",
          description: Optional[
            MultiLanguageTextType
          ] = MultiLanguageTextType(
            dict_={
              "en": "Unambigous identification number of a DocumentVersion."
            }
          ),
          semantic_id: Optional[Reference] = ExternalReference(
            key=(
                Key(
                  type_=KeyTypes.GLOBAL_REFERENCE,
                  value="0173-1#02-AAO100#002",
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
                type_="Cardinality",
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
          value: LangStringSet,
          id_short: Optional[str] = "Title",
          value_id: Optional[Reference] = None,
          display_name: Optional[MultiLanguageNameType] = None,
          category: Optional[str] = "PARAMETER",
          description: Optional[
            MultiLanguageTextType
          ] = MultiLanguageTextType(
            dict_={
              "en": "List of language-dependent titles of the Document. Constraint: For each language-depended Title a Summary and at least one KeyWord shall exist for the given language."
            }
          ),
          semantic_id: Optional[Reference] = ExternalReference(
            key=(
                Key(
                  type_=KeyTypes.GLOBAL_REFERENCE,
                  value="0173-1#02-AAO105#002",
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
                type_="Cardinality",
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

      class SubTitle(MultiLanguageProperty):
        def __init__(
          self,
          value: LangStringSet,
          id_short: Optional[str] = "SubTitle",
          value_id: Optional[Reference] = None,
          display_name: Optional[MultiLanguageNameType] = None,
          category: Optional[str] = "PARAMETER",
          description: Optional[
            MultiLanguageTextType
          ] = MultiLanguageTextType(
            dict_={
              "en": "List of language-dependent subtitles of the Document."
            }
          ),
          semantic_id: Optional[Reference] = ExternalReference(
            key=(
                Key(
                  type_=KeyTypes.GLOBAL_REFERENCE,
                  value="0173-1#02-ABH998#001",
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
                type_="Cardinality",
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

      class Summary(MultiLanguageProperty):
        def __init__(
          self,
          value: LangStringSet,
          id_short: Optional[str] = "Summary",
          value_id: Optional[Reference] = None,
          display_name: Optional[MultiLanguageNameType] = None,
          category: Optional[str] = "PARAMETER",
          description: Optional[
            MultiLanguageTextType
          ] = MultiLanguageTextType(
            dict_={
              "en": "List of language-dependent summaries of the Document. Constraint: For each language-depended Summary a Title and at least one KeyWord shall exist for the given language."
            }
          ),
          semantic_id: Optional[Reference] = ExternalReference(
            key=(
                Key(
                  type_=KeyTypes.GLOBAL_REFERENCE,
                  value="0173-1#02-AAO106#002",
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
                type_="Cardinality",
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
          value: LangStringSet,
          id_short: Optional[str] = "KeyWords",
          value_id: Optional[Reference] = None,
          display_name: Optional[MultiLanguageNameType] = None,
          category: Optional[str] = "PARAMETER",
          description: Optional[
            MultiLanguageTextType
          ] = MultiLanguageTextType(
            dict_={
              "en": "List of language-dependent keywords of the Document. Note: Mutiple keywords are given as comma separated list for each language. Constraint: For each language-depended KeyWord a Title and Summary shall exist for the given language. Note: This can be intentionally a blank."
            }
          ),
          semantic_id: Optional[Reference] = ExternalReference(
            key=(
                Key(
                  type_=KeyTypes.GLOBAL_REFERENCE,
                  value="0173-1#02-ABH999#001",
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
                type_="Cardinality",
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
          display_name: Optional[MultiLanguageNameType] = None,
          category: Optional[str] = "PARAMETER",
          description: Optional[
            MultiLanguageTextType
          ] = MultiLanguageTextType(
            dict_={
              "en": "Date when the document status was set. Format is YYYY-MM-dd."
            }
          ),
          semantic_id: Optional[Reference] = ExternalReference(
            key=(
                Key(
                  type_=KeyTypes.GLOBAL_REFERENCE,
                  value="0173-1#02-ABI000#001",
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
                type_="Cardinality",
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
          display_name: Optional[MultiLanguageNameType] = None,
          category: Optional[str] = "PARAMETER",
          description: Optional[
            MultiLanguageTextType
          ] = MultiLanguageTextType(
            dict_={
              "en": "Each document version represents a point in time in the document life cycle. This status value refers to the milestones in the document life cycle. The following two values should be used for the application of this guideline: InReview (under review), Released (released)"
            }
          ),
          semantic_id: Optional[Reference] = ExternalReference(
            key=(
                Key(
                  type_=KeyTypes.GLOBAL_REFERENCE,
                  value="0173-1#02-ABI001#001",
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
                type_="Cardinality",
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

      class OrganizationName(Property):
        def __init__(
          self,
          value: str,
          id_short: Optional[str] = "OrganizationName",
          value_type: DataTypeDefXsd = str,
          value_id: Optional[Reference] = None,
          display_name: Optional[MultiLanguageNameType] = None,
          category: Optional[str] = "PARAMETER",
          description: Optional[
            MultiLanguageTextType
          ] = MultiLanguageTextType(
            dict_={
              "en": "Organiziation short name of the author of the Document."
            }
          ),
          semantic_id: Optional[Reference] = ExternalReference(
            key=(
                Key(
                  type_=KeyTypes.GLOBAL_REFERENCE,
                  value="0173-1#02-ABI002#001",
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
                type_="Cardinality",
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
          display_name: Optional[MultiLanguageNameType] = None,
          category: Optional[str] = "PARAMETER",
          description: Optional[
            MultiLanguageTextType
          ] = MultiLanguageTextType(
            dict_={
              "en": "Official name of the organization of author of the Document."
            }
          ),
          semantic_id: Optional[Reference] = ExternalReference(
            key=(
                Key(
                  type_=KeyTypes.GLOBAL_REFERENCE,
                  value="0173-1#02-ABI004#001",
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
                type_="Cardinality",
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

      class DigitalFile(SubmodelElementCollection):
        class MimeType(Property):
          def __init__(
            self,
            value: str,
            id_short: Optional[str] = "MimeType",
            value_type: DataTypeDefXsd = str,
            value_id: Optional[Reference] = None,
            display_name: Optional[MultiLanguageNameType] = None,
            category: Optional[str] = "PARAMETER",
            description: Optional[
              MultiLanguageTextType
            ] = MultiLanguageTextType(
              dict_={
                "en": "The MIME-Type classifies the data of massage."
              }
            ),
            semantic_id: Optional[Reference] = ExternalReference(
              key=(
                  Key(
                    type_=KeyTypes.GLOBAL_REFERENCE,
                    value="0173-1#02-AAO214#002 ",
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
                  type_="Cardinality",
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

        class DocumentPath(Property):
          def __init__(
            self,
            value: str,
            id_short: Optional[str] = "DocumentPath",
            value_type: DataTypeDefXsd = str,
            value_id: Optional[Reference] = None,
            display_name: Optional[MultiLanguageNameType] = None,
            category: Optional[str] = "PARAMETER",
            description: Optional[
              MultiLanguageTextType
            ] = MultiLanguageTextType(
              dict_={"en": "The document path leads to the document."}
            ),
            semantic_id: Optional[Reference] = ExternalReference(
              key=(
                  Key(
                    type_=KeyTypes.GLOBAL_REFERENCE,
                    value="0173-1#02-ABI005#001 ",
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
                  type_="Cardinality",
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
          mimeType: Union[str, MimeType],
          documentPath: Union[str, DocumentPath],
          id_short: Optional[str] = "DigitalFile",
          display_name: Optional[MultiLanguageNameType] = None,
          category: Optional[str] = None,
          description: Optional[
            MultiLanguageTextType
          ] = MultiLanguageTextType(
            dict_={
              "en": "Note: each DigitalFile represents the same content or Document version, but can be provided in different technical formats (PDF, PDFA, html..) or by a link."
            }
          ),
          semantic_id: Optional[Reference] = ExternalReference(
            key=(
                Key(
                  type_=KeyTypes.GLOBAL_REFERENCE,
                  value="0173-1#02-ABI504#001/0173-1#01-AHF583#001",
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
                type_="Cardinality",
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

          # Build a submodel element if a raw value was passed in the argument
          if mimeType and not isinstance(mimeType, SubmodelElement):
            mimeType = self.MimeType(mimeType)

          # Build a submodel element if a raw value was passed in the argument
          if documentPath and not isinstance(documentPath, SubmodelElement):
            documentPath = self.DocumentPath(documentPath)

          # Add all passed/initialized submodel elements to a single list
          embedded_submodel_elements = []
          for se_arg in [mimeType, documentPath]:
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

      class PreviewFile(SubmodelElementCollection):
        class MimeType(Property):
          def __init__(
            self,
            value: str,
            id_short: Optional[str] = "MimeType",
            value_type: DataTypeDefXsd = str,
            value_id: Optional[Reference] = None,
            display_name: Optional[MultiLanguageNameType] = None,
            category: Optional[str] = "PARAMETER",
            description: Optional[
              MultiLanguageTextType
            ] = MultiLanguageTextType(
              dict_={
                "en": "The MIME-Type classifies the data of massage."
              }
            ),
            semantic_id: Optional[Reference] = ExternalReference(
              key=(
                  Key(
                    type_=KeyTypes.GLOBAL_REFERENCE,
                    value="0173-1#02-AAO214#002 ",
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
                  type_="Cardinality",
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

        class DocumentPath(Property):
          def __init__(
            self,
            value: str,
            id_short: Optional[str] = "DocumentPath",
            value_type: DataTypeDefXsd = str,
            value_id: Optional[Reference] = None,
            display_name: Optional[MultiLanguageNameType] = None,
            category: Optional[str] = "PARAMETER",
            description: Optional[
              MultiLanguageTextType
            ] = MultiLanguageTextType(
              dict_={"en": "The document path leads to the document."}
            ),
            semantic_id: Optional[Reference] = ExternalReference(
              key=(
                  Key(
                    type_=KeyTypes.GLOBAL_REFERENCE,
                    value="0173-1#02-ABI005#001 ",
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
                  type_="Cardinality",
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
          mimeType: Union[str, MimeType],
          documentPath: Union[str, DocumentPath],
          id_short: Optional[str] = "PreviewFile",
          display_name: Optional[MultiLanguageNameType] = None,
          category: Optional[str] = "PARAMETER",
          description: Optional[
            MultiLanguageTextType
          ] = MultiLanguageTextType(
            dict_={
              "en": "Provides a preview image of the DocumentVersion, e.g. first page, in a commonly used image format and low resolution. Note: low resolution e.g. < 512 x 512 pixels. Constraint: the MIME type needs to match the file type. Allowed file types are JPG, PNG, BMP."
            }
          ),
          semantic_id: Optional[Reference] = ExternalReference(
            key=(
                Key(
                  type_=KeyTypes.GLOBAL_REFERENCE,
                  value="0173-1#02-ABI505#001 /0173-1#01-AHF584#001",
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
                type_="Cardinality",
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

          # Build a submodel element if a raw value was passed in the argument
          if mimeType and not isinstance(mimeType, SubmodelElement):
            mimeType = self.MimeType(mimeType)

          # Build a submodel element if a raw value was passed in the argument
          if documentPath and not isinstance(documentPath, SubmodelElement):
            documentPath = self.DocumentPath(documentPath)

          # Add all passed/initialized submodel elements to a single list
          embedded_submodel_elements = []
          for se_arg in [mimeType, documentPath]:
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

      class RefersTo(ReferenceElement):
        def __init__(
          self,
          value: Reference,
          id_short: Optional[str] = "RefersTo",
          display_name: Optional[MultiLanguageNameType] = None,
          category: Optional[str] = "PARAMETER",
          description: Optional[
            MultiLanguageTextType
          ] = MultiLanguageTextType(
            dict_={
              "en": 'Forms a generic RefersTo-relationship to another Document or DocumentVersion. They have a loose relationship. Constraint: reference targets a SMC "Document" or a “DocumentVersion”.'
            }
          ),
          semantic_id: Optional[Reference] = ExternalReference(
            key=(
                Key(
                  type_=KeyTypes.GLOBAL_REFERENCE,
                  value="0173-1#02-ABI006#001",
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
                type_="Cardinality",
                value_type=str,
                value="ZeroToMany",
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

      class BasedOn(ReferenceElement):
        def __init__(
          self,
          value: Reference,
          id_short: Optional[str] = "BasedOn",
          display_name: Optional[MultiLanguageNameType] = None,
          category: Optional[str] = "PARAMETER",
          description: Optional[
            MultiLanguageTextType
          ] = MultiLanguageTextType(
            dict_={
              "en": 'Forms a BasedOn-relationship to another Document or DocumentVersion. Typically states, that the content of the document bases on another document (e.g. specification requirements). Both have a strong relationship. Constraint: reference targets a SMC "Document" or a “DocumentVersion”.'
            }
          ),
          semantic_id: Optional[Reference] = ExternalReference(
            key=(
                Key(
                  type_=KeyTypes.GLOBAL_REFERENCE,
                  value="0173-1#02-ABI007#001",
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
                type_="Cardinality",
                value_type=str,
                value="ZeroToMany",
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

      class TranslationOf(ReferenceElement):
        def __init__(
          self,
          value: Reference,
          id_short: Optional[str] = "TranslationOf",
          display_name: Optional[MultiLanguageNameType] = None,
          category: Optional[str] = "PARAMETER",
          description: Optional[
            MultiLanguageTextType
          ] = MultiLanguageTextType(
            dict_={
              "en": 'Forms a TranslationOf-relationship to another Document or DocumentVersion. Both have a strong relationship. Constaint: The (language independent) content must be identical in both documents or document versions. Constraint: reference targets a SMC "Document" or a “DocumentVersion”.'
            }
          ),
          semantic_id: Optional[Reference] = ExternalReference(
            key=(
                Key(
                  type_=KeyTypes.GLOBAL_REFERENCE,
                  value="0173-1#02-ABI008#001",
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
                type_="Cardinality",
                value_type=str,
                value="ZeroToMany",
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
        language: Iterable[Union[str, Language]],
        documentVersionId: Union[str, DocumentVersionId],
        title: Union[LangStringSet, Title],
        summary: Union[LangStringSet, Summary],
        keyWords: Union[LangStringSet, KeyWords],
        statusSetDate: Union[Date, StatusSetDate],
        statusValue: Union[str, StatusValue],
        organizationName: Union[str, OrganizationName],
        organizationOfficialName: Union[str, OrganizationOfficialName],
        digitalFile: Iterable[DigitalFile],
        subTitle: Optional[Union[LangStringSet, SubTitle]] = None,
        previewFile: Optional[PreviewFile] = None,
        refersTo: Optional[Iterable[Union[Reference, RefersTo]]] = None,
        basedOn: Optional[Iterable[Union[Reference, BasedOn]]] = None,
        translationOf: Optional[
          Iterable[Union[Reference, TranslationOf]]
        ] = None,
        id_short: Optional[str] = "DocumentVersion",
        display_name: Optional[MultiLanguageNameType] = None,
        category: Optional[str] = "PARAMETER",
        description: Optional[MultiLanguageTextType] = MultiLanguageTextType(
          dict_={
            "en": "Information elements of individual VDI 2770 DocumentVersion entities. Note: at the time of handover, this collection shall include at least one DocumentVersion."
          }
        ),
        semantic_id: Optional[Reference] = ExternalReference(
          key=(
              Key(
                type_=KeyTypes.GLOBAL_REFERENCE,
                value="0173-1#02-ABI503#001/0173-1#01-AHF582#001*01",
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
              type_="Cardinality",
              value_type=str,
              value="ZeroToMany",
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
        if language and all([isinstance(i, str) for i in language]):
          language = [self.Language(i) for i in language]

        # Build a submodel element if a raw value was passed in the argument
        if documentVersionId and not isinstance(
          documentVersionId, SubmodelElement
        ):
          documentVersionId = self.DocumentVersionId(documentVersionId)

        # Build a submodel element if a raw value was passed in the argument
        if title and not isinstance(title, SubmodelElement):
          title = self.Title(title)

        # Build a submodel element if a raw value was passed in the argument
        if subTitle and not isinstance(subTitle, SubmodelElement):
          subTitle = self.SubTitle(subTitle)

        # Build a submodel element if a raw value was passed in the argument
        if summary and not isinstance(summary, SubmodelElement):
          summary = self.Summary(summary)

        # Build a submodel element if a raw value was passed in the argument
        if keyWords and not isinstance(keyWords, SubmodelElement):
          keyWords = self.KeyWords(keyWords)

        # Build a submodel element if a raw value was passed in the argument
        if statusSetDate and not isinstance(statusSetDate, SubmodelElement):
          statusSetDate = self.StatusSetDate(statusSetDate)

        # Build a submodel element if a raw value was passed in the argument
        if statusValue and not isinstance(statusValue, SubmodelElement):
          statusValue = self.StatusValue(statusValue)

        # Build a submodel element if a raw value was passed in the argument
        if organizationName and not isinstance(
          organizationName, SubmodelElement
        ):
          organizationName = self.OrganizationName(organizationName)

        # Build a submodel element if a raw value was passed in the argument
        if organizationOfficialName and not isinstance(
          organizationOfficialName, SubmodelElement
        ):
          organizationOfficialName = self.OrganizationOfficialName(
            organizationOfficialName
          )

        # Build a list of submodel elements if a raw values were passed in the argument
        if refersTo and all([isinstance(i, Reference) for i in refersTo]):
          refersTo = [self.RefersTo(i) for i in refersTo]

        # Build a list of submodel elements if a raw values were passed in the argument
        if basedOn and all([isinstance(i, Reference) for i in basedOn]):
          basedOn = [self.BasedOn(i) for i in basedOn]

        # Build a list of submodel elements if a raw values were passed in the argument
        if translationOf and all(
          [isinstance(i, Reference) for i in translationOf]
        ):
          translationOf = [self.TranslationOf(i) for i in translationOf]

        # Add all passed/initialized submodel elements to a single list
        embedded_submodel_elements = []
        for se_arg in [
          language,
          documentVersionId,
          title,
          subTitle,
          summary,
          keyWords,
          statusSetDate,
          statusValue,
          organizationName,
          organizationOfficialName,
          digitalFile,
          previewFile,
          refersTo,
          basedOn,
          translationOf,
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

    class DocumentedEntity(ReferenceElement):
      def __init__(
        self,
        value: Reference,
        id_short: Optional[str] = "DocumentedEntity",
        display_name: Optional[MultiLanguageNameType] = None,
        category: Optional[str] = "PARAMETER",
        description: Optional[MultiLanguageTextType] = MultiLanguageTextType(
          dict_={
            "en": "Identifies entities, which are subject to the Document. Note: can be omitted, if the subject of the Document is the overall Asset of the Asset Administration Shell. Note: if no Entity according clause 2.2 is referenced, this ReferenceElement is not required at all. Note: This mechanism substitutes the ObjectId-provision of the VDI2770 (see section 2.2 and appendix B)."
          }
        ),
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
              type_="Cardinality",
              value_type=str,
              value="ZeroToMany",
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
      documentId: Iterable[DocumentId],
      documentClassification: Iterable[DocumentClassification],
      documentVersion: Optional[Iterable[DocumentVersion]] = None,
      documentedEntity: Optional[
        Iterable[Union[Reference, DocumentedEntity]]
      ] = None,
      id_short: Optional[str] = "Document",
      display_name: Optional[MultiLanguageNameType] = None,
      category: Optional[str] = None,
      description: Optional[MultiLanguageTextType] = MultiLanguageTextType(
        dict_={
          "en": "Each SMC describes a Document (see IEC 82045-1 and IEC 8245-2), which is associated to the particular Asset Administration Shell."
        }
      ),
      semantic_id: Optional[Reference] = ExternalReference(
        key=(
            Key(
              type_=KeyTypes.GLOBAL_REFERENCE,
              value="0173-1#02-ABI500#001/0173-1#01-AHF579#001*01",
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
            type_="Cardinality",
            value_type=str,
            value="ZeroToMany",
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
      if documentedEntity and all(
        [isinstance(i, Reference) for i in documentedEntity]
      ):
        documentedEntity = [self.DocumentedEntity(i) for i in documentedEntity]

      # Add all passed/initialized submodel elements to a single list
      embedded_submodel_elements = []
      for se_arg in [
        documentId,
        documentClassification,
        documentVersion,
        documentedEntity,
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

  class Entity(Entity):
    def __init__(
      self,
      id_short: Optional[str] = "Entity",
      entity_type: EntityType = EntityType.CO_MANAGED_ENTITY,
      statement: Iterable[SubmodelElement] = (),
      global_asset_id: Optional[str] = None,
      specific_asset_id: Iterable[SpecificAssetId] = (),
      display_name: Optional[MultiLanguageNameType] = None,
      category: Optional[str] = "PARAMETER",
      description: Optional[MultiLanguageTextType] = MultiLanguageTextType(
        dict_={
          "en": "States, that the described Entity is an important entity for documentation of the superordinate Asset of the Asset Administration Shell. Note: typically, such Entities are well-identified sub-parts of the Asset, such as supplier parts delivered to the manufacturer of the Asset."
        }
      ),
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
      embedded_data_specifications: Iterable[EmbeddedDataSpecification] = None,
    ):
      if qualifier is None:
        qualifier = (
          Qualifier(
            type_="Cardinality",
            value_type=str,
            value="ZeroToMany",
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
    id_: str,
    numberOfDocuments: Union[int, NumberOfDocuments],
    document: Optional[Iterable[Document]] = None,
    entity: Optional[Iterable[Entity]] = None,
    id_short: Optional[str] = "HandoverDocumentation",
    display_name: Optional[MultiLanguageNameType] = None,
    category: Optional[str] = None,
    description: Optional[MultiLanguageTextType] = MultiLanguageTextType(
      dict_={
        "en": "The Submodel defines a set meta data for the handover of documentation from the manufacturer to the operator for industrial equipment."
      }
    ),
    administration: Optional[AdministrativeInformation] = AdministrativeInformation(
      version="1",
      revision="2",
      creator=None,
      template_id=None,
      embedded_data_specifications=[],
    ),
    semantic_id: Optional[Reference] = ModelReference(
      key=(Key(type_=KeyTypes.SUBMODEL, value="0173-1#01-AHF578#001"),),
      type_=Submodel,
      referred_semantic_id=None,
    ),
    qualifier: Iterable[Qualifier] = None,
    kind: ModellingKind = ModellingKind.TEMPLATE,
    extension: Iterable[Extension] = (),
    supplemental_semantic_id: Iterable[Reference] = (),
    embedded_data_specifications: Iterable[EmbeddedDataSpecification] = None,
  ):
    if qualifier is None:
      qualifier = ()

    if embedded_data_specifications is None:
      embedded_data_specifications = []

    # Build a submodel element if a raw value was passed in the argument
    if numberOfDocuments and not isinstance(numberOfDocuments, SubmodelElement):
      numberOfDocuments = self.NumberOfDocuments(numberOfDocuments)

    # Add all passed/initialized submodel elements to a single list
    embedded_submodel_elements = []
    for se_arg in [numberOfDocuments, document, entity]:
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


if __name__ == "__main__":
  handover_documentation = HandoverDocumentation(
    id_="0173-1#01-AHF578#001",
    numberOfDocuments=1,
    document=[
      HandoverDocumentation.Document(
        documentId=[
          HandoverDocumentation.Document.DocumentId(
            documentDomainId="SOME_DOMAIN",
            valueId="SOME_VALUE"
          )
        ],
        documentClassification=[
          HandoverDocumentation.Document.DocumentClassification(
            classId="CLASS_ID_123",
            className="Class Name",
            classificationSystem="Classification System Name"
          )
        ],
        documentVersion=[
          HandoverDocumentation.Document.DocumentVersion(
            language=["en"],
            documentVersionId="v1.0",
            title=HandoverDocumentation.Document.Title(
              dict_={"en": "Document Title"}
            ),
            summary=HandoverDocumentation.Document.Summary(
              dict_={"en": "Document Summary"}
            ),
            keyWords=HandoverDocumentation.Document.KeyWords(
              dict_={"en": "Keyword1, Keyword2"}
            ),
            statusSetDate="2023-10-01",
            statusValue="Draft",
            organizationName="Organization Name",
            organizationOfficialName="Official Organization Name",
            digitalFile=[
              HandoverDocumentation.Document.DigitalFile(
                value=Reference(
                  key=(
                    Key(type_=KeyTypes.GLOBAL_REFERENCE, value="https://example.com/some_pdf.pdf"),
                  )
                )
              )
            ],
          )
        ],
      )
    ],
    entity=[
      HandoverDocumentation.Entity(
        id_short="Entity1",
        specific_asset_id=[SpecificAssetId(value="Specific Asset ID")],
      )
    ],
  )
