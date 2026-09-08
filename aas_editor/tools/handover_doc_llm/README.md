# Handover Documentation tool

The Handover Documentation Tool is an extension of the AAS Manager that allows users to generate a Handover Documentation Submodel from a given PDF file with the usage of LLMs.

## Usage

- Select the "Handover Documentation tool" from the "Tools" menu.
- In the opened dialog, select the LLM provider and model you want to use.
- For cloud providers: provide your API key. For Ollama: optionally provide a custom base URL.
- Select the embedding provider to use for RAG on large documents. For Ollama embeddings, optionally specify a custom embedding model and base URL.
- Drag and drop or select the PDF file you want to use.
- Check and adjust the extracted data if necessary.
- The Handover Documentation Submodel will be added to the current AAS file or a new file.

## How it works

The tool uses the [LangChain](https://python.langchain.com/docs/) library for interaction with LLMs.
For large documents it splits the PDF into smaller chunks, stores them in a FAISS vector store, and uses a RAG chain to query the LLM with the relevant context. Small documents are passed directly to the LLM without RAG.

## Supported LLM providers

| Provider | Type | Requires |
|----------|------|----------|
| OpenAI | Cloud API | API key |
| Anthropic | Cloud API | API key |
| Google Vertex | Cloud API | API key |
| Groq | Cloud API | API key |
| Mistral AI | Cloud API | API key |
| **Ollama** | **Local** | [Ollama](https://ollama.com) installed & running |

### Using Ollama (local LLMs)

1. Install [Ollama](https://ollama.com) and start the server.
2. Pull a model, e.g.: `ollama pull llama3.2`
3. Select **Ollama** as the LLM provider in the dialog.
4. Enter the model name (e.g. `llama3.2`). Leave the Base URL empty to use the default (`http://localhost:11434`).
5. Select **Ollama** as the embedding provider. Optionally enter a custom embedding model name (default: `nomic-embed-text`) and base URL.
6. Pull the embedding model: `ollama pull nomic-embed-text`

Recommended models for this task: `llama3.2`, `qwen2.5`, `mistral`.

## Supported embedding providers

| Provider | Type | Notes |
|----------|------|-------|
| HuggingFace | Local | Default; uses `sentence-transformers/all-mpnet-base-v2`; no key required |
| OpenAI | Cloud API | Requires a separate OpenAI API key |
| Ollama | Local | Custom model (default: `nomic-embed-text`) and base URL configurable |

The embedding provider is selected automatically based on the chosen LLM provider but can be changed manually.

## Disclaimer

The Handover Documentation tool relies on Large Language Models for information extraction. LLMs may produce incomplete, inaccurate, or inconsistent results. Always verify the extracted documentation before use in production or compliance-relevant contexts.
