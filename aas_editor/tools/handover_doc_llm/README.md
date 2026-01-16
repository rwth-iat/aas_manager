# Handover Documentation tool

The Handover Documentation Tool is a extension of the AAS Manager that allows users to generate a Handover Documentation from a given PDF file with the usage of LLMs.

Usage:
- Select the "Handover Documentation tool" from the "Tools" menu.
- In the opened dialog, select the LLM provider and model you want to use.
- Provide your API key for the selected LLM provider.
- Drag and drop or select the PDF file you want to use.
- Check and adjust the extracted data if necessary.
- The Handover Documentation will be added to the current AAS file.

The tool uses the [LangChain](https://python.langchain.com/docs/) library for the interaction with LLMs.
It splits the PDF into smaller chunks and uses vector stores to store the chunks.
After that, it uses a RAG chain to query the LLM with the data.


The tool currently supports the following LLM providers:
- OpenAI
- Anthropic
- Google Vertex
- Groq
- Mistral AI

Disclaimer: The Handover Documentation tool relies on Large Language Models for information extraction. LLMs may produce incomplete, inaccurate, or inconsistent results. Always verify the extracted documentation before use in production or compliance-relevant contexts.



The Handover Documentation Tool is a extension of the AAS Manager that allows users to generate a Handover Documentation Submodel from a given PDF file with the usage of LLMs.

Usage:
- Select the LLM provider and model you want to use.
- Provide your API key for the selected LLM provider.
- Drag and drop or select the PDF file you want to use.
- Check and adjust the extracted data if necessary.
- The Handover Documentation Submodel will be added to the current AAS file or a new file.
