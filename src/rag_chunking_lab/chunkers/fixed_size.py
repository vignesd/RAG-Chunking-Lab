
from langchain_text_splitters import CharacterTextSplitter

from ..logging_config import get_logger

logger = get_logger(__name__)

SAMPLE_TEXT = """
Fixed-size chunking is the most traditional and simplest method of breaking down documents. 
It divides text into chunks of a predefined maximum character or token length. 
While easy to implement, it often results in split sentences, cut-off context, and separated semantic concepts. 
Despite these drawbacks, it remains useful for high-speed processing pipelines where precision is less critical than raw throughput.
"""


def fixed_chunk(text: str = ""):
    logger.info("=== Starting Fixed-Size Chunking Demo ===")
    if not text:
        text = SAMPLE_TEXT

    # Initialize Fixed-Size Character Text Splitter
    splitter = CharacterTextSplitter(
        separator="",          # Split character by character if needed
        chunk_size=100,        # Maximum characters per chunk
        chunk_overlap=20,      # Overlap characters between chunks to preserve context
        length_function=len
    )

    logger.info("Splitting sample text...")
    chunks = splitter.create_documents([text])

    print("\n" + "=" * 50)
    print(f"FIXED-SIZE CHUNKS (Total: {len(chunks)})")
    print("=" * 50)
    for i, chunk in enumerate(chunks, 1):
        print(f"\n[Chunk {i}] Length: {len(chunk.page_content)}")
        print(f"Content: {repr(chunk.page_content)}")
