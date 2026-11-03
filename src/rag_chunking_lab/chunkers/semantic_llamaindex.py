from __future__ import annotations

from typing import Any

from langchain_core.documents import Document
from llama_index.core import Document as LlamaDocument
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.ollama import OllamaEmbedding

from ..logging_config import get_logger

logger = get_logger(__name__)


def semantic_chunk_llamaindex(
    text: str,
    *,
    model: str = "embeddinggemma-2:270m",
    base_url: str = "http://localhost:11434",
    breakpoint_percentile: int = 85,
    buffer_size: int = 1,
    metadata: dict[str, Any] | None = None,
) -> list[Document]:
    """Return LlamaIndex semantic nodes converted to LangChain Documents.

    LlamaIndex's semantic parser does not expose a maximum character chunk
    size. Apply a secondary size-aware splitter if a hard limit is required.
    """
    if not text or not text.strip():
        logger.warning("LlamaIndex received empty text.")
        return []
    if not 1 <= breakpoint_percentile <= 100:
        raise ValueError("breakpoint_percentile must be between 1 and 100")
    if buffer_size < 1:
        raise ValueError("buffer_size must be at least 1")

    logger.info(
        "Starting LlamaIndex semantic chunking: model=%s percentile=%d buffer=%d",
        model, breakpoint_percentile, buffer_size,
    )
    embed_model = OllamaEmbedding(model_name=model, base_url=base_url)
    splitter = SemanticSplitterNodeParser(
        embed_model=embed_model,
        breakpoint_percentile_threshold=breakpoint_percentile,
        buffer_size=buffer_size,
    )
    source = LlamaDocument(text=text, metadata=dict(metadata or {}))
    nodes = splitter.get_nodes_from_documents([source])

    base_metadata = dict(metadata or {})
    documents: list[Document] = []
    for index, node in enumerate(nodes):
        content = node.get_content().strip()
        if not content:
            continue
        node_metadata = dict(base_metadata)
        for key, value in node.metadata.items():
            node_metadata.setdefault(key, value)
        node_metadata.update({
            "chunking_method": "llamaindex_semantic",
            "chunk_index": index,
        })
        documents.append(
            Document(page_content=content, metadata=node_metadata))

    logger.info("LlamaIndex generated %d chunks.", len(documents))
    print("\n" + "=" * 60)
    print(f"RESULTS: Generated {len(documents)} Semantic Chunks (LlamaIndex)")
    print("=" * 60)

    for idx, chunk in enumerate(documents, start=1):
        print(
            f"\n[Chunk {idx}] Character Length: {len(chunk.page_content)}")
        print("-" * 40)
        print(chunk.page_content.strip())
        print("-" * 40)

    return documents
