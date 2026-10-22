# Handover Documentation tool

The Handover Documentation Tool is an extension of the AAS Manager that allows users to generate a Handover Documentation Submodel from a given PDF file with the usage of LLMs.

## Usage

- Select the "Handover Documentation tool" from the "Tools" menu.
- In the opened dialog, select the LLM provider and model you want to use.
- For cloud providers: provide your API key. For Ollama: optionally provide a custom base URL.
- Drag and drop or select the PDF file you want to use.
- Check and adjust the extracted data if necessary.
- The Handover Documentation Submodel will be added to the current AAS file or a new file.

## How it works

The tool uses the [LangChain](https://python.langchain.com/docs/) library for interaction with LLMs.
It sends the text of the first and last pages of the PDF (3 + 3 by default, adjustable in the dialog) directly to the LLM. The text is capped at 60,000 characters.

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

Recommended models for this task: `llama3.2`, `qwen2.5`, `mistral`.

## Disclaimer

The Handover Documentation tool relies on Large Language Models for information extraction. LLMs may produce incomplete, inaccurate, or inconsistent results. Always verify the extracted documentation before use in production or compliance-relevant contexts.
