import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter

from logger_config import get_logger

logger = get_logger(__name__)

SAMPLE_TEXT = """
Recursive chunking is the gold-standard default approach for text parsing in modern RAG systems. 
It attempts to split text hierarchically using a list of separators (typically paragraphs, sentences, and words).

If a chunk is too large after splitting by paragraphs, it moves down to split by sentences. 
This ensures that natural language structures like sentences and paragraphs are kept intact as much as possible within the target token limit.
"""


def recursive_chunk(text: str = ""):
    logger.info("=== Starting Recursive Chunking Demo ===")
    if not text:
        text = SAMPLE_TEXT

    # Initialize Recursive Character Text Splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=150,       # Target maximum size per chunk
        chunk_overlap=30,     # Overlap to maintain context continuity
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    logger.info("Executing recursive split...")
    # print("ORIGINAL TEXT")
    # print(text)
    # print("="*50)
    chunks = splitter.create_documents([text])

    print("\n" + "=" * 50)
    print(f"RECURSIVE CHUNKS (Total: {len(chunks)})")
    print("=" * 50)
    for i, chunk in enumerate(chunks, 1):
        print(f"\n[Chunk {i}]")
        print(chunk.page_content.strip())
