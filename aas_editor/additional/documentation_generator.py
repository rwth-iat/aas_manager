import json

from basyx.aas.adapter.json import AASToJsonEncoder
from basyx.aas.model import LangStringSet
from basyx.aas.model.datatypes import Date

from aas_editor.additional.handover import HandoverDocumentation

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

    documentID = HandoverDocumentation.Document.DocumentId(
        isPrimary=obj['document']['documentId'].get('isPrimary', None),
        documentDomainId=obj['document']['documentId'].get('documentDomainId', ''),
        valueId=obj['document']['documentId'].get('valueId', ''))

    documentClassification = HandoverDocumentation.Document.DocumentClassification(
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

    digitalFile = HandoverDocumentation.Document.DocumentVersion.DigitalFile(
        mimeType=obj['document']['documentVersion'].get('digitalFile', {}).get('mimeType', ''),
        documentPath=obj['document']['documentVersion'].get('digitalFile', {}).get('documentPath', ''))

    documentVersion = HandoverDocumentation.Document.DocumentVersion(
        language=language,
        documentVersionId=obj['document']['documentVersion'].get('documentVersionId', ''),
        title=(
            {} if not (result := {
                lang: obj['document']['documentVersion'].get('title', [''])[i]
                for i, lang in enumerate(language)
                if i < len(obj['document']['documentVersion'].get('title', []))
            }) else LangStringSet(result)
        ),
        summary=(
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
        organizationName=obj['document']['documentVersion'].get('organizationName', ''),
        organizationOfficialName=obj['document']['documentVersion'].get('organizationOfficialName', ''),
        digitalFile=[digitalFile] if digitalFile.MimeType or digitalFile.DocumentPath else [],
        subTitle=(
            {} if not (result := {
                lang: obj['document']['documentVersion'].get('subTitle', [''])[i]
                for i, lang in enumerate(language)
                if i < len(obj['document']['documentVersion'].get('subTitle', []))
            }) else LangStringSet(result)
        )
    )

    document = HandoverDocumentation.Document(
        documentId=[documentID],
        documentClassification=[documentClassification],
        documentVersion=[documentVersion]
    )

    handover_documentation = HandoverDocumentation(
        id_=obj.get('id', 0),
        numberOfDocuments=int(obj.get('numberOfDocuments', 0)),
        document=[document]
    )

    return handover_documentation


if __name__ == "__main__":
    data = """```json
{
  "id": "222-101",
  "numberOfDocuments": 1,
  "document": {
    "documentId": {
      "documentDomainId": "example_company",
      "valueId": "222-101",
      "isPrimary": true
    },
    "documentClassification": {
      "classId": "HandoverDocumentation",
      "className": ["Handover Documentation"],
      "classificationSystem": "VDI2770:2018"
    },
    "documentVersion": {
      "language": ["de"],
      "documentVersionId": "1",
      "title": ["Datensheet"],
      "subTitle": [],
      "summary": ["Datensheet für 222-101"],
      "keyWords": ["example_company", "222-101"],
      "statusSetDate": "2025-09-22",
      "statusValue": "Released",
      "organizationName": "example_company",
      "organizationOfficialName": "example_company GmbH",
      "digitalFile": {
        "mimeType": "application/pdf",
        "documentPath": "https://www.example.com/222-101"
      }
    }
  }
}
```"""
    print(json.dumps(json2handover_documentation(data), cls=AASToJsonEncoder, indent=2))
