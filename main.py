from chunkings.fixed_size import fixed_chunk
from chunkings.recursive import recursive_chunk
from chunkings.document_specific import document_chunk
from chunkings.semantic import semantic_chunk
from chunkings.semantic_lang import semantic_chunk_lang
from chunkings.agentic import agentic_chunk
from chunkings.agentic_open import agentic_chunk_open
from pathlib import Path
from logger_config import get_logger, setup_logging
setup_logging()


logger = get_logger(__name__)


def main(option: int = 1):
    file_path = Path("semantic_text.txt")
    sample_text = file_path.read_text(encoding="utf-8")
    print("="*50)
    print("ORIGINAL TEXT")
    print("="*50)
    print(sample_text)
    print("="*50)
    if option == 1:
        fixed_chunk(sample_text)
    elif option == 2:
        recursive_chunk(sample_text)
    elif option == 3:
        document_chunk(sample_text)
    elif option == 4:
        semantic_chunk(sample_text)
    elif option == 5:
        semantic_chunk_lang(sample_text)
    elif option == 6:
        agentic_chunk_open(sample_text)
    else:
        agentic_chunk(sample_text)


if __name__ == "__main__":
    option = int(input("""
    Enter the chunk method?(1/2/3/4/5)
    1-Fixed Chunking.
    2-Recursive Chunking.
    3-Document Chunking(.md).
    4-Semantic Chunking(OpenAI).
    5-Semantic Chunking(Langchain)
    6-Agentic Chunking (open).
    7-Agentic Chunking
    \n"""))
    main(option)
