# semantic_chunking.py
import os
import numpy as np
from langchain_openai import OpenAIEmbeddings
from logger_config import get_logger

logger = get_logger(__name__)


def cosine_similarity(v1, v2) -> float:
    """Calculate cosine similarity between two embedding vectors."""
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))


def semantic_chunk(text: str, threshold: float = 0.55):
    """
    Splits text into semantic chunks by generating OpenAI embeddings 
    for each sentence and detecting semantic topic shifts.
    """
    logger.info("Starting semantic chunking execution...")
    logger.info(
        "Initializing OpenAI Embeddings model (text-embedding-3-small)...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    raw_sentences = [s.strip() for s in text.replace(
        "\n", " ").split(".") if len(s.strip()) > 10]
    if not raw_sentences:
        logger.warning("No valid sentences found in the provided text.")
        return []

    logger.info(f"Split input text into {len(raw_sentences)} sentences.")
    logger.info("Generating vector embeddings via OpenAI API...")
    sentence_vectors = embeddings.embed_documents(raw_sentences)

    chunks = []
    current_chunk = [raw_sentences[0]]

    for i in range(len(sentence_vectors) - 1):
        sim = cosine_similarity(sentence_vectors[i], sentence_vectors[i + 1])

        if sim < threshold:
            # Topic shift detected: close current chunk and start a new one
            chunks.append(" ".join(current_chunk) + ".")
            current_chunk = [raw_sentences[i + 1]]
        else:
            current_chunk.append(raw_sentences[i + 1])

    if current_chunk:
        chunks.append(" ".join(current_chunk) + ".")

    logger.info(f"Successfully generated {len(chunks)} semantic chunks.")
    print("\n" + "=" * 50)
    print(f"SEMANTICALLY GROUPED CHUNKS (Total: {len(chunks)})")
    print("=" * 50)
    for i, chunk in enumerate(chunks, 1):
        print(f"\n[Chunk {i}]")
        print(chunk)
