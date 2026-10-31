import logging
from langchain_text_splitters import MarkdownHeaderTextSplitter

from logger_config import get_logger

logger = get_logger(__name__)

MARKDOWN_DOCUMENT = """
# Project Overview
This document outlines the core architecture of our AI pipeline.

## Backend Infrastructure
We utilize Python, UV for fast package management, and SQLite for lightweight metadata tracking.

### Database Layer
All vector embeddings are indexed locally using ChromaDB for sub-millisecond similarity matching.

## Frontend Interface
The application interface is served locally via VS Code extensions and custom web components.
"""


def document_chunk(text: str = ""):
    logger.info("=== Starting Document-Specific (Markdown) Chunking Demo ===")
    if not text:
        text = MARKDOWN_DOCUMENT

    # Define structural boundaries to split on
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]

    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on)

    logger.info("Parsing markdown document structure...")
    # print("ORIGINAL TEXT")
    # print(MARKDOWN_DOCUMENT)
    # print("="*50)

    chunks = splitter.split_text(text)

    print("\n" + "=" * 50)
    print(f"DOCUMENT-SPECIFIC CHUNKS (Total: {len(chunks)})")
    print("=" * 50)
    for i, chunk in enumerate(chunks, 1):
        print(f"\n[Chunk {i}] Metadata Headers: {chunk.metadata}")
        print(f"Content:\n{chunk.page_content.strip()}")
