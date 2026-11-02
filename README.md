# RAG Chunking Lab

RAG Chunking Lab is a small Python project for exploring and comparing text chunking strategies used to prepare documents for retrieval-augmented generation (RAG) systems.

## Chunking strategies

Run the project and choose one of the available methods:

| Option | Strategy | How it works |
| --- | --- | --- |
| 1 | Fixed-size | Splits text into character-sized chunks with overlap. |
| 2 | Recursive | Splits using progressively smaller separators to preserve text structure where possible. |
| 3 | Markdown-aware | Splits Markdown by heading and includes heading metadata. |
| 4 | Semantic | Uses LangChain's `SemanticChunker` with OpenAI embeddings to find semantic boundaries. |
| 5 | Agentic | Uses an OpenAI chat model to decide whether adjacent paragraphs belong in separate chunks. |

The demo reads its input from `data/examples/sample_document.md`. `data/examples/semantic_text.txt` is also included as a sample text document.

## Requirements

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/)
- An OpenAI API key for the semantic and agentic strategies.

## Setup

Install the project dependencies:

```shell
uv sync
```

Copy `.env.example` to `.env` in the project root and add your API key:

```dotenv
OPENAI_API_KEY=your-api-key
```

Keep the key private. `.env` files are excluded from Git.

## Run

```shell
uv run python -m rag_chunking_lab
```

Enter an option from 1 to 5 when prompted. The selected strategy prints its chunks to the console. Semantic and agentic chunking make OpenAI API requests and may incur usage charges.

## Project layout

```text
.
├── data/
│   └── examples/       # Input text and sample Markdown
├── src/
│   └── rag_chunking_lab/
│       ├── chunkers/   # Individual chunking implementations
│       ├── __main__.py # Interactive demo entry point
│       └── logging_config.py
├── pyproject.toml
└── uv.lock
```
