prompt = """
{context}
You are given a single PDF document containing data relevant to Asset Administration Shell (AAS) Submodels, specifically following the VDI 2770 guideline for Handover Documentation.

Your task is to extract the following data from the PDF file:
id,
numberOfDocuments,
documentDomainId: "Identification of the domain in which the given DocumentId is unique. The domain ID can e.g., be the name or acronym of the providing organisation.",
valueId: "Identification number of the Document within a given domain, e.g. the providing organisation.",
isPrimary: "Flag indicating that a DocumentId within a collection of at least two DocumentId`s is the 'primary' identifier for the document. This is the preferred ID of the document (commonly from the point of view of the owner of the asset). Note: can be omitted, if the ID is not primary. Note: can be omitted, if only one ID is for a Document. Contraint: only one DocumentId in a collection may be marked as primary.",
classId: "Unique ID of the document class within a ClassficationSystem. Constraint: If ClassificationSystem is set to "VDI2770:2018", the given IDs of VDI2770:2018 shall be used"
className: "List of language-dependent names of the selected ClassID. Constraint: If ClassificationSystem is set to "VDI2770:2018" then the given names of VDI2770:2018 need be used. Constraint: languages shall match at least the language specifications of the included DocumentVersions (below).",
classificationSystem: "Identification of the classification system. For classifications according VDI 2270 always set to "VDI2770:2018". Further classification systems are commonly used, such as "IEC61355-1:2008".",
language: "This property contains a list of languages used within the DocumentVersion. Each property codes one language identification according to ISO 639-1 or ISO 639-2 used in the Document." It must be a list of two characters,
documentVersionId: "Unambigous identification number of a DocumentVersion.",
title: "List of language-dependent titles of the Document. Constraint: For each language-depended Title a Summary and at least one KeyWord shall exist for the given language.",
subTitle: "List of language-dependent subtitles of the Document.",
summary: "List of language-dependent summaries of the Document. Constraint: For each language-depended Summary a Title and at least one KeyWord shall exist for the given language.",
keyWords: "List of language-dependent keywords of the Document. Note: Mutiple keywords are given as comma separated list for each language. Constraint: For each language-depended KeyWord a Title and Summary shall exist for the given language. Note: This can be intentionally a blank.",
statusSetDate: "Date when the document status was set. Format is YYYY-MM-dd.",
statusValue: "Each document version represents a point in time in the document life cycle. This status value refers to the milestones in the document life cycle. The following two values should be used for the application of this guideline: InReview (under review), Released (released)",
organizationName: "Organiziation short name of the author of the Document.",
organizationOfficalName: "Official name of the organization of author of the Document.",
mimeType: "The MIME-Type classifies the data of massage.",
documentPath: "The document path leads to the document."

Steps:
1. Parse the given context and find for all attributes the best fitting value.
2. Output the result strictly as one single .json file. Do not include any explanation or additional text. Make sure that the file is properly escaped and quoted according to JSON standards.

Output columns should be:
id, numberOfDocuments, document.documentId.documentDomainId, document.documentId.valueId, document.documentId.isPrimary, document.documentClassification.classId, document.documentClassification.className, document.documentClassification.classificationSystem, document.documentVersion.language, document.documentVersion.documentVersionId, document.documentVersion.title, document.documentVersion.subTitle, document.documentVersion.summary , document.documentVersion.keyWords, document.documentVersion.statusSetDate, document.documentVersion.statusValue, document.documentVersion.organizationName, document.documentVersion.organizationOfficialName, document.documentVersion.digitalFile.mimeType, document.documentVersion.digitalFile.documentPath

Make reasonable assumptions where exact fields are not available, but clearly align to the HandoverDocumentation structure and if nothing was found answer with an empty entry (no "").
"""