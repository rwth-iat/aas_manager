def _init_openai_chat(model, key):
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(model=model, api_key=key)


def _init_anthropic_chat(model, key):
    from langchain_anthropic import ChatAnthropic
    return ChatAnthropic(model=model, api_key=key)


def _init_vertex_chat(model, key):
    from langchain_google_vertexai import ChatVertexAI
    return ChatVertexAI(model=model, api_key=key)


def _init_groq_chat(model, key):
    from langchain_groq import ChatGroq
    return ChatGroq(model=model, api_key=key)


def _init_mistral_chat(model, key):
    from langchain_mistralai import ChatMistralAI
    return ChatMistralAI(model=model, api_key=key)


def _init_ollama_chat(model, key):
    from langchain_ollama import ChatOllama
    base_url = key if key else "http://localhost:11434"
    return ChatOllama(model=model, base_url=base_url)


def _init_ollama_embeddings(key, model="nomic-embed-text"):
    from langchain_ollama import OllamaEmbeddings
    base_url = key if key else "http://localhost:11434"
    return OllamaEmbeddings(model=model or "nomic-embed-text", base_url=base_url)


def _init_hf_embeddings(_key, _model=None):
    from langchain_huggingface import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")


def _init_openai_embeddings(key, _model=None):
    from langchain_openai import OpenAIEmbeddings
    return OpenAIEmbeddings(api_key=key)

TOOL_DESCRIPTION = \
"""The Tool allows users to generate a Handover Documentation Submodel from a given PDF file with the usage of LLMs.

Usage:
- Select the LLM provider and model you want to use.
- Provide your API key for the selected LLM provider.
- Drag and drop or select the PDF file you want to use.
- Check and adjust the extracted data if necessary.
- The extracted data will be emitted as a HandoverDocumentation Submodel.
- The submodel will be added to the current or newly created AAS file.

Please consider that the following properties will be not be extracted and have to be provided manually if required:
- DocumentVersion: RefersToEntities, BasedOnReferences, TranslationOfEntities, PreviewFile
"""

LLM_PROVIDERS = {
    "OpenAI": {
        "default_model": "gpt-40-mini",
        "init": _init_openai_chat,
    },
    "Anthropic": {
        "default_model": "claude-3-5-sonnet-latest",
        "init": _init_anthropic_chat,
    },
    "Google Vertex": {
        "default_model": "gemini-1.5-flash",
        "init": _init_vertex_chat,
    },
    "Groq": {
        "default_model": "llama-3.3-70b-versatile",
        "init": _init_groq_chat,
    },
    "Mistral AI": {
        "default_model": "mistral-large-latest",
        "init": _init_mistral_chat,
    },
    "Ollama": {
        "default_model": "llama3.2",
        "init": _init_ollama_chat,
    },
}

EMBEDDING_PROVIDERS = {
    "HuggingFace": {
        "default_model": "",
        "init": _init_hf_embeddings,
    },
    "OpenAI": {
        "default_model": "",
        "init": _init_openai_embeddings,
    },
    "Ollama": {
        "default_model": "nomic-embed-text",
        "init": _init_ollama_embeddings,
    },
}

PROMPT = """
{context}
You are given a single PDF document from which you need to extract information according to the VDI 2770 guideline for Handover Documentation.

Your task is to extract the following data from the PDF file:
#DocumentId:
- documentDomainId: "Identification of the domain in which the given DocumentId is unique. The domain ID can e.g., be the name or acronym of the providing organisation."
- documentIdentifier: "alphanumeric character sequence uniquely identifying a document"
#DocumentClassification
- classId: "This is very important field. ID of the document class according to VDI 2770 classification system. Possible values are:
    ID - Document class name
    "01-01" - Identification
    "02-01" - Technical specification
    "02-02" - Drawings, plans
    "02-03" - Assemblies
    "02-04" - Certificates, declarations
    "03-01" - Commissioning, de-commissioning
    "03-02" - Operation
    "03-03" - General safety
    "03-04" - Inspection, maintenance, testing
    "03-05" - Repair
    "03-06" - Spare parts
    "04-01" - Contract documents

#DocumentVersion
- title: "Language-dependent titles of the Document. E.g. {{'en': 'Operating Manual', 'de': 'Betriebsanleitung'}}."
- subTitle (optional): "Language-dependent subtitles of the Document. E.g. {{'en': 'For Model XYZ', 'de': 'Für Modell XYZ'}}."
- description: "Language-dependent descriptions of the Document. E.g. {{'en': 'This document describes...', 'de': 'Dieses Dokument beschreibt...'}}."
- keyWords: "Language-dependent keywords of the Document with multiple keywords separated by commas. E.g. {{'en': 'manual,operation', 'de': 'Handbuch,Bedienung'}}."
    Constraint: For each language-depended Title a Description and at least one KeyWord shall exist for the given language!,

- version: "Unambiguous identification number of a DocumentVersion."
- language: "List of languages (codes according to ISO 639-1) used in the Document. e.g., ['en', 'de', 'fr']"
- statusSetDate: "Date when the document status was set. Format is YYYY-MM-dd."
- statusValue: "InReview or Released"
- organizationShortName: "Short name of the author organization."
- organizationOfficialName: "Official name of the organization of author of the Document."

Steps:
1. Parse the given context and find for all attributes the best fitting value.
2. Output the result strictly as one single .json file. Do not include any explanation or additional text. Make sure that the file is properly escaped and quoted according to JSON standards.

Output columns should be:
document.documentId.documentDomainId: str,
document.documentId.documentIdentifier: str,

document.documentClassification.classId: str,

document.documentVersion.title: Dict[str, str],
document.documentVersion.subTitle: Dict[str, str],
document.documentVersion.description: Dict[str, str],
document.documentVersion.keyWords: Dict[str, str],
document.documentVersion.version: str,
document.documentVersion.language: List[str],
document.documentVersion.statusSetDate: str,
document.documentVersion.statusValue: str,
document.documentVersion.organizationShortName: str,
document.documentVersion.organizationOfficialName: str

Make reasonable assumptions where exact fields are not available, but clearly align to the HandoverDocumentation structure and if nothing was found answer with an empty entry (no "").
"""
RESPONSE_SCHEMA = r"""
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "DocumentResponse",
  "type": "object",
  "required": ["document"],
  "additionalProperties": false,
  "properties": {
    "document": {
      "type": "object",
      "required": ["documentId", "documentClassification", "documentVersion"],
      "additionalProperties": false,
      "properties": {
        "documentId": {
          "type": "object",
          "required": ["documentDomainId", "documentIdentifier"],
          "additionalProperties": false,
          "properties": {
            "documentDomainId": { "type": "string", "minLength": 1 },
            "documentIdentifier": { "type": "string", "minLength": 1 }
          }
        },
        "documentClassification": {
          "type": "object",
          "required": ["classId"],
          "additionalProperties": false,
          "properties": {
            "classId": { "type": "string", "minLength": 1 }
          }
        },
        "documentVersion": {
          "type": "object",
          "required": [
            "title", "subTitle", "description", "keyWords",
            "version", "language", "statusSetDate", "statusValue",
            "organizationShortName", "organizationOfficialName"
          ],
          "additionalProperties": false,
          "properties": {
            "title": { "type": "object", "additionalProperties": { "type": "string" } },
            "subTitle": { "type": "object", "additionalProperties": { "type": "string" } },
            "description": { "type": "object", "additionalProperties": { "type": "string" } },
            "keyWords": { "type": "object", "additionalProperties": { "type": "string" } },
            "version": { "type": "string", "pattern": "^[0-9]+(\\.[0-9]+)*$" },
            "language": {
              "type": "array",
              "items": { "type": "string", "minLength": 2 },
              "minItems": 1,
              "uniqueItems": true
            },
            "statusSetDate": { "type": "string", "format": "date-time" },
            "statusValue": { "type": "string", "minLength": 1 },
            "organizationShortName": { "type": "string", "minLength": 1 },
            "organizationOfficialName": { "type": "string", "minLength": 1 }
          }
        }
      }
    }
  }
}
"""