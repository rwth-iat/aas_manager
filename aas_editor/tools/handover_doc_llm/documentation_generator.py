#  Copyright (C) 2025  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/

import json

from basyx.aas.adapter.json import AASToJsonEncoder
from basyx.aas.model import LangStringSet, ModellingKind
from basyx.aas.model.datatypes import Date

from aas_editor.tools.handover_doc_llm.handover_submodel import HandoverDocumentation

def json2handover_documentation(json_str: str) -> HandoverDocumentation | None:
    """
    Convert a JSON string to a HandoverDocumentation object.

    :param json_str: JSON string.
    :return: HandoverDocumentation object.
    """
    json_str = json_str[json_str.find("{"):json_str.rfind("}") + 1]
    try:
        obj = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

    language = obj['document']['documentVersion'].get('language', [''])

    date = obj['document']['documentVersion'].get('statusSetDate', '').split('-')

    documentID = HandoverDocumentation.Documents.Documents_item.DocumentIds.Documentids_item(
        documentIsPrimary=obj['document']['documentId'].get('isPrimary', None),
        documentDomainId=obj['document']['documentId'].get('documentDomainId', ''),
        documentIdentifier=obj['document']['documentId'].get('valueId', ''))

    documentClassification = HandoverDocumentation.Documents.Documents_item.DocumentClassifications.Documentclassifications_item(
        classId=obj['document']['documentClassification'].get('classId', ''),
        className=(
            {} if not (result := {
                lang: obj['document']['documentVersion'].get('className', [''])[i]
                for i, lang in enumerate(language)
                if i < len(obj['document']['documentVersion'].get('className', []))
            }) else LangStringSet(result)
        ),
        classificationSystem=obj['document']['documentClassification'].get('classificationSystem', ''),
    )

    digitalFile = HandoverDocumentation.Documents.Documents_item.DocumentVersions.Documentversions_item.DigitalFiles.Digitalfiles_item(
        value="SOME_PATH")


    documentVersion = HandoverDocumentation.Documents.Documents_item.DocumentVersions.Documentversions_item(
        language=language,
        version=obj['document']['documentVersion'].get('documentVersionId', ''),
        title=(
            {} if not (result := {
                lang: obj['document']['documentVersion'].get('title', [''])[i]
                for i, lang in enumerate(language)
                if i < len(obj['document']['documentVersion'].get('title', []))
            }) else LangStringSet(result)
        ),
        subtitle=(
            {} if not (result := {
                lang: obj['document']['documentVersion'].get('subTitle', [''])[i]
                for i, lang in enumerate(language)
                if i < len(obj['document']['documentVersion'].get('subTitle', []))
            }) else LangStringSet(result)
        ),
        description_=(
            {} if not (result := {
                lang: obj['document']['documentVersion'].get('summary', [''])[i]
                for i, lang in enumerate(language)
                if i < len(obj['document']['documentVersion'].get('summary', []))
            }) else LangStringSet(result)
        ),
        keyWords=(
            {} if not (result := {
                lang: obj['document']['documentVersion'].get('keyWords', [''])[i]
                for i, lang in enumerate(language)
                if i < len(obj['document']['documentVersion'].get('keyWords', []))
            }) else LangStringSet(result)
        ),
        statusSetDate=Date(int(date[0]), int(date[1]), int(date[2])) if len(date) == 3 and all(
            part.isdigit() for part in date) else None,
        statusValue=obj['document']['documentVersion'].get('statusValue', ''),
        organizationShortName=obj['document']['documentVersion'].get('organizationName', ''),
        organizationOfficialName=obj['document']['documentVersion'].get('organizationOfficialName', ''),
        digitalFiles=HandoverDocumentation.Documents.Documents_item.DocumentVersions.Documentversions_item.DigitalFiles([digitalFile])
    )

    document = HandoverDocumentation.Documents.Documents_item(
        documentIds=HandoverDocumentation.Documents.Documents_item.DocumentIds([documentID]),
        documentClassifications=HandoverDocumentation.Documents.Documents_item.DocumentClassifications([documentClassification]),
        documentVersions=HandoverDocumentation.Documents.Documents_item.DocumentVersions([documentVersion]),
        documentedEntities=HandoverDocumentation.Documents.Documents_item.DocumentedEntities([])
    )

    handover_documentation = HandoverDocumentation(
        id_=obj.get('id', 0),
        documents=HandoverDocumentation.Documents([document]),
        entities=HandoverDocumentation.Entities([]),
        kind = ModellingKind.INSTANCE
    )

    return handover_documentation


if __name__ == "__main__":
    data = """```json
{
  "id": "222-101",
  "document": {
    "documentId": {
      "documentDomainId": "example_company",
      "documentIdentifier": "222-101",
      "isPrimary": true
    },
    "documentClassification": {
      "classId": "HandoverDocumentation",
      "className": ["Handover Documentation"],
      "classificationSystem": "VDI2770:2018"
    },
    "documentVersion": {
      "language": ["de"],
      "version": "1",
      "title": ["Datensheet"],
      "subTitle": [],
      "description": ["Datensheet für 222-101"],
      "keyWords": ["example_company", "222-101"],
      "statusSetDate": "2025-09-22",
      "statusValue": "Released",
      "organizationShortName": "example_company",
      "organizationOfficialName": "example_company GmbH"
    }
  }
}
```"""
    print(json.dumps(json2handover_documentation(data), cls=AASToJsonEncoder, indent=2))
