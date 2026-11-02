
from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_core.documents import Document
from ..logging_config import get_logger

logger = get_logger(__name__)


def semantic_chunk(text: str) -> list[Document]:
    """
    Splits text semantically using LangChain's native SemanticChunker 
    powered by OpenAI embeddings and dynamic percentile breakpoints.
    """
    logger.info("Initializing LangChain SemanticChunker execution...")
    model_name = "embeddinggemma-2:270m"

    logger.info(
        f"Initializing OpenAI Embeddings model ({model_name})...")
    # embeddinggemma-2:270m
    # embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    embeddings = OllamaEmbeddings(
        model="embeddinggemma-2:270m",
        base_url="http://localhost:11434",)

    # breakpoint_threshold_type can be 'percentile', 'standard_deviation', or 'interquartile'
    text_splitter = SemanticChunker(
        embeddings=embeddings,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=85
    )

    logger.info(
        "Executing semantic distance calculations and chunking via LangChain...")
    docs = text_splitter.create_documents([text])

    logger.info(
        f"Successfully generated {len(docs)} semantic chunks using LangChain.")

    print("\n" + "=" * 60)
    print(f"RESULTS: Generated {len(docs)} Semantic Chunks (LangChain)")
    print("=" * 60)

    for idx, chunk in enumerate(docs[:10], start=1):
        print(f"\n[Chunk {idx}] Character Length: {len(chunk.page_content)}")
        print("-" * 40)
        print(chunk.page_content.strip())
        print("-" * 40)
    return docs
