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
from basyx.aas.model import ModellingKind
from basyx.aas.model.datatypes import Date

from tools.handover_doc_llm.handover_submodel import HandoverDocumentation

MIME_TYPE = "application/pdf"

DocumentClassificationVDI2770 = {
    "01-01": {
        "classId": "01-01",
        "className": {
            "en": "Identification",
            "de": "Identifikation"},
        "semanticId": "0173-1#07-ABU484#003",
    },
    "02-01": {
        "classId": "02-01",
        "className": {
            "en": "Technical specification",
            "de": "Technische Spezifikation"},
        "semanticId": "0173-1#07-ABU485#003",
    },
    "02-02": {
        "classId": "02-02",
        "className": {
            "en": "Drawings, plans",
            "de": "Zeichnungen, Pläne"},
        "semanticId": "0173-1#07-ABU486#003",
    },
    "02-03": {
        "classId": "02-03",
        "className": {
            "en": "Assemblies",
            "de": "Bauteile"},
        "semanticId": "0173-1#07-ABU487#003",
    },
    "02-04": {
        "classId": "02-04",
        "className": {
            "en": "Certificates, declarations",
            "de": "Zeugnisse, Zertifikate, Bescheinigungen"},
        "semanticId": "0173-1#07-ABU488#003",
    },
    "03-01": {
        "classId": "03-01",
        "className": {
            "en": "Commissioning, de-commissioning",
            "de": "Montage, Demontage"},
        "semanticId": "0173-1#07-ABU489#003",
    },
    "03-02": {
        "classId": "03-02",
        "className": {
            "en": "Operation",
            "de": "Bedienung"},
        "semanticId": "0173-1#07-ABU490#003",
    },
    "03-03": {
        "classId": "03-03",
        "className": {
            "en": "General safety",
            "de": "AllgemeineSicherheit"},
        "semanticId": "0173-1#07-ABU491#003",
    },
    "03-04": {
        "classId": "03-04",
        "className": {
            "en": "Inspection, maintenance, testing",
            "de": "Inspektion, Wartung, Prüfung"},
        "semanticId": "0173-1#07-ABU492#003",
    },
    "03-05": {
        "classId": "03-05",
        "className": {
            "en": "Repair",
            "de": "Instandsetzung"},
        "semanticId": "0173-1#07-ABU493#003",
    },
    "03-06": {
        "classId": "03-06",
        "className": {
            "en": "Spare parts",
            "de": "Ersatzteile"},
        "semanticId": "0173-1#07-ABU494#003",
    },
    "04-01": {
        "classId": "04-01",
        "className": {
            "en": "Contract documents",
            "de": "Vertragsunterlagen"},
        "semanticId": "0173-1#07-ABU495#003",
    }
}

def json2document(json_str: str):
    """
    Convert a JSON string to documents and entities.

    :param json_str: JSON string.
    :return: Tuple of documents and entities.
    """
    json_str = json_str[json_str.find("{"):json_str.rfind("}") + 1]
    try:
        obj = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

    from aas_editor.tools.handover_doc_llm.handover_submodel import HandoverDocumentation

    documentID = HandoverDocumentation.Documents.Documents_item.DocumentIds.Documentids_item(
        documentIsPrimary=True, #TODO: Fix me
        documentDomainId=obj['document']['documentId'].get('documentDomainId', ''),
        documentIdentifier=obj['document']['documentId'].get('valueId', ''))

    classId = obj['document']['documentClassification'].get('classId', '')
    documentClassification = HandoverDocumentation.Documents.Documents_item.DocumentClassifications.Documentclassifications_item(
        classId=classId,
        className=DocumentClassificationVDI2770[classId]['className'] if classId in DocumentClassificationVDI2770 else {},
        classificationSystem="VDI 2770 Blatt 1:2020",
    )

    digitalFile = HandoverDocumentation.Documents.Documents_item.DocumentVersions.Documentversions_item.DigitalFiles.Digitalfiles_item(
        value="SOME_PATH", #TODO: Fix me
        content_type=MIME_TYPE)

    statusSetDate = obj['document']['documentVersion'].get('statusSetDate', '').split('-')
    if len(statusSetDate) == 3 and all(part.isdigit() for part in statusSetDate):
        statusSetDate = Date(int(statusSetDate[0]), int(statusSetDate[1]), int(statusSetDate[2]))
    else:
        statusSetDate = None


    documentVersion = HandoverDocumentation.Documents.Documents_item.DocumentVersions.Documentversions_item(
        language=obj['document']['documentVersion'].get('language', ['']),
        version=obj['document']['documentVersion'].get('documentVersionId', ''),
        title=obj['document']['documentVersion'].get('title'),
        subtitle=obj['document']['documentVersion'].get('subTitle'),
        description_=obj['document']['documentVersion'].get('description'),
        keyWords=obj['document']['documentVersion'].get('keyWords'),
        statusSetDate=statusSetDate,
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

    return document


def documents2handover_documentation(documents, id_: str = "0"):
    """
    Convert documents to a HandoverDocumentation object.

    :param documents: Documents object.
    :param id_: ID of the HandoverDocumentation.
    :return: HandoverDocumentation object.
    """
    handover_documentation = HandoverDocumentation(
        id_=id_,
        documents=HandoverDocumentation.Documents(documents),
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
      "classId": "03-04"
    },
    "documentVersion": {
      "language": ["de"],
      "version": "1",
      "title": {"de":"Datensheet", "en":"Datasheet"},
      "subTitle": {},
      "description": {"de": "Datensheet für 222-101", "en":"Datasheet for 222-101"},
      "keyWords": {"de": ["example_company", "222-101"], "en": ["example_company", "222-101"]},
      "statusSetDate": "2025-09-22",
      "statusValue": "Released",
      "organizationShortName": "example_company",
      "organizationOfficialName": "example_company GmbH"
    }
  }
}
```"""
    documents = [json2document(data)]
    handover_doc = documents2handover_documentation(documents, "1")
    print(json.dumps(handover_doc, cls=AASToJsonEncoder, indent=4))

