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
You are given a single PDF document containing data relevant to Asset Administration Shell (AAS) Submodels, specifically following the VDI 2770 guideline for Handover Documentation.

Your task is to extract the following data from the PDF file:
id,

#DocumentId:
documentDomainId: "Identification of the domain in which the given DocumentId is unique. The domain ID can e.g., be the name or acronym of the providing organisation.",
documentIdentifier: "alphanumeric character sequence uniquely identifying a document"
documentIsPrimary: "Flag indicating that a DocumentId within a collection of at least two DocumentId`s is the 'primary' identifier for the document. This is the preferred ID of the document (commonly from the point of view of the owner of the asset). Note: can be omitted, if the ID is not primary. Note: can be omitted, if only one ID is for a Document. Contraint: only one DocumentId in a collection may be marked as primary.",

#DocumentClassification
classId: "Unique ID of the document class within a ClassficationSystem. Constraint: If ClassificationSystem is set to "VDI2770:2018", the given IDs of VDI2770:2018 shall be used"
className: "List of language-dependent names of the selected ClassID. Constraint: If ClassificationSystem is set to "VDI2770:2018" then the given names of VDI2770:2018 need be used. Constraint: languages shall match at least the language specifications of the included DocumentVersions (below).",
classificationSystem: "Identification of the classification system. For classifications according VDI 2270 always set to "VDI2770:2018". Further classification systems are commonly used, such as "IEC61355-1:2008".",

#DocumentVersion
title: "List of language-dependent titles of the Document. Constraint: For each language-depended Title a Summary and at least one KeyWord shall exist for the given language.",
subTitle: "List of language-dependent subtitles of the Document.",
description: "List of language-dependent descriptions of the Document. Constraint: For each language-depended Summary a Title and at least one KeyWord shall exist for the given language.",
keyWords: "List of language-dependent keywords of the Document. Note: Mutiple keywords are given as comma separated list for each language. Constraint: For each language-depended KeyWord a Title and Summary shall exist for the given language. Note: This can be intentionally a blank.",
version: "Unambigous identification number of a DocumentVersion.",
language: "List of languages used within the DocumentVersion. Each property codes one language identification according to ISO 639-1 or ISO 639-2 used in the Document." It must be a list of two characters,
statusSetDate: "Date when the document status was set. Format is YYYY-MM-dd.",
statusValue: "InReview or Released",
organizationShortName: "Short name of the author organization.",
organizationOfficalName: "Official name of the organization of author of the Document.",

Steps:
1. Parse the given context and find for all attributes the best fitting value.
2. Output the result strictly as one single .json file. Do not include any explanation or additional text. Make sure that the file is properly escaped and quoted according to JSON standards.

Output columns should be:
id, 
document.documentId.documentDomainId, 
document.documentId.documentIdentifier, 
document.documentId.documentIsPrimary, 

document.documentClassification.classId, 
document.documentClassification.className, 
document.documentClassification.classificationSystem,

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
