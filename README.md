# RAG Chunking Lab

RAG Chunking Lab is a small Python project for exploring and comparing text chunking strategies used to prepare documents for retrieval-augmented generation (RAG) systems. The interactive demo runs each strategy against `data/examples/semantic_text.txt`.

## Chunking strategies

Run the demo and select one of the available strategies:

| Option | Strategy | How it works |
| --- | --- | --- |
| 1 | Fixed-size | Splits text into character-sized chunks with overlap. |
| 2 | Recursive | Splits using progressively smaller separators to preserve text structure where possible. |
| 3 | Markdown-aware | Splits Markdown by heading and includes heading metadata. |
| 4 | LangChain semantic | Uses LangChain's `SemanticChunker` with Ollama embeddings. |
| 5 | Cosine-similarity semantic | Groups sentences using consecutive embedding distances and chunk-size limits. |
| 6 | Hybrid semantic | Combines semantic boundaries with chunk-size handling. |
| 7 | Chonkie semantic | Uses Chonkie's `SemanticChunker` with Ollama embeddings and a character-counting adapter. |
| 8 | LlamaIndex semantic | Uses LlamaIndex's `SemanticSplitterNodeParser` with Ollama embeddings. It does not enforce a maximum chunk size. |
| 9 | Agentic | Uses an OpenAI chat model to decide whether adjacent paragraphs belong in separate chunks. |

Semantic strategies 4–8 use the `embeddinggemma-2:270m` model from a local Ollama server by default (`http://localhost:11434`). The Chonkie implementation defaults to a 2,400-character chunk size and a similarity threshold of `0.85`; LlamaIndex defaults to a breakpoint percentile of `80` and a buffer size of `1`. The chunkers return LangChain `Document` objects.

## Requirements

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com/) with the `embeddinggemma-2:270m` model for semantic strategies 4–8
- An OpenAI API key for the agentic strategy (option 9) only

## Setup

Install the project dependencies:

```shell
uv sync
```

For semantic strategies 4–8, start Ollama and make sure the configured embedding model is available:

```shell
ollama pull embeddinggemma-2:270m
```

For agentic chunking, copy `.env.example` to `.env` in the project root and set your API key:

```dotenv
OPENAI_API_KEY=your-api-key
```

Keep the key private. `.env` files are excluded from Git.

## Run

```shell
uv run python -m rag_chunking_lab
```

Enter an option from 1 to 9 when prompted. The selected strategy prints its chunks to the console. Semantic strategies use the local Ollama service; agentic chunking makes OpenAI API requests and may incur usage charges.

## Project layout

```text
.
├── data/
│   └── examples/                     # Documents used to try chunkers
│       ├── sample_document.md        # Sample Markdown document
│       ├── semantic_long.txt         # Longer semantic chunking input
│       ├── semantic_long2.md         # Longer Markdown input
│       ├── semantic_short.txt        # Short semantic chunking input
│       ├── semantic_text.txt         # Default input for the interactive demo
│       └── single_paragraph.txt      # Single-paragraph input
├── src/
│   └── rag_chunking_lab/
│       ├── __init__.py                # Package initialization
│       ├── __main__.py                # Interactive strategy menu and runner
│       ├── logging_config.py          # Environment-configurable logging
│       └── chunkers/
│           ├── __init__.py            # Chunker package initialization
│           ├── agentic.py             # OpenAI-assisted paragraph boundaries
│           ├── fixed_size.py          # Fixed-size chunks with overlap
│           ├── markdown.py            # Markdown-aware chunks with headings
│           ├── recursive.py           # Recursive separator-based splitting
│           ├── semantic.py            # LangChain, cosine-similarity, and hybrid methods
│           ├── semantic_chonkie.py    # Chonkie semantic chunker with Ollama embeddings
│           └── semantic_llamaindex.py # LlamaIndex semantic splitter with Ollama embeddings
├── tests/
│   └── cosin_similarity.py            # Exploratory embedding similarity script
├── .env.example                       # Example environment and logging settings
├── .gitignore                         # Files excluded from Git
├── .python-version                    # Project's Python version for uv
├── main.py                            # Standalone chunker experiment script
├── pyproject.toml                     # Package metadata and dependencies
├── README.md                          # Project overview and usage
└── uv.lock                            # Locked dependency versions
```

`src/rag_chunking_lab/__main__.py` is the recommended entry point. The scripts under `tests/` and the repository-root `main.py` are standalone experiments rather than the interactive application or a configured automated test suite.
