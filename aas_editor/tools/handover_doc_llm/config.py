from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain_google_vertexai import ChatVertexAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

TOOL_DESCRIPTION = """
The Tool allows users to generate a Handover Documentation Submodel from a given PDF file with the usage of LLMs.

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
        "init": lambda model, key: ChatOpenAI(model=model, api_key=key),
    },
    "Anthropic": {
        "default_model": "claude-3-5-sonnet-latest",
        "init": lambda model, key: ChatAnthropic(model=model, api_key=key),
    },
    "Google Vertex": {
        "default_model": "gemini-1.5-flash",
        "init": lambda model, key: ChatVertexAI(model=model, api_key=key),
    },
    "Groq": {
        "default_model": "llama-3.3-70b-versatile",
        "init": lambda model, key: ChatGroq(model=model, api_key=key),
    },
    "Mistral AI": {
        "default_model": "mistral-large-latest",
        "init": lambda model, key: ChatMistralAI(model=model, api_key=key),
    },
}

EMBEDDING_PROVIDERS = {
    "default": lambda key: HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2"),
    "huggingface": lambda key: HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2"),
    "OpenAI": lambda key: OpenAIEmbeddings(api_key=key),
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
- title: "Language-dependent titles of the Document as a dict. E.g. {{'en': 'Operating Manual', 'de': 'Betriebsanleitung'}}.
- subTitle (optional): "Language-dependent subtitles of the Document. E.g. {{'en': 'For Model XYZ', 'de': 'Für Modell XYZ'}}."
- description: "List of language-dependent descriptions of the Document. E.g. {{'en': 'This document describes...', 'de': 'Dieses Dokument beschreibt...'}}."
- keyWords: "List of language-dependent keywords of the Document. E.g. {{'en': 'manual,operation', 'de': 'Handbuch,Bedienung'}}."
    Constraint: For each language-depended Title a Description and at least one KeyWord shall exist for the given language!,

- version: "Unambigous identification number of a DocumentVersion."
- language: "List of languages used within the DocumentVersion. Each property codes one language identification according to ISO 639-1 or ISO 639-2 used in the Document. It must be a list of two characters"
- statusSetDate: "Date when the document status was set. Format is YYYY-MM-dd."
- statusValue: "InReview or Released"
- organizationShortName: "Short name of the author organization."
- organizationOfficalName: "Official name of the organization of author of the Document."

Steps:
1. Parse the given context and find for all attributes the best fitting value.
2. Output the result strictly as one single .json file. Do not include any explanation or additional text. Make sure that the file is properly escaped and quoted according to JSON standards.

Output columns should be:
document.documentId.documentDomainId, 
document.documentId.documentIdentifier, 

document.documentClassification.classId, 

document.documentVersion.title, 
document.documentVersion.subTitle, 
document.documentVersion.description, 
document.documentVersion.keyWords, 
document.documentVersion.version, 
document.documentVersion.language, 
document.documentVersion.statusSetDate, 
document.documentVersion.statusValue, 
document.documentVersion.organizationShortName, 
document.documentVersion.organizationOfficialName, 

Make reasonable assumptions where exact fields are not available, but clearly align to the HandoverDocumentation structure and if nothing was found answer with an empty entry (no "").
"""
