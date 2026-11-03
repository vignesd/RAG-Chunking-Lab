# type:ignore
from __future__ import annotations

import logging
import math
from typing import Any, Callable

from chonkie import BaseEmbeddings, SemanticChunker
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from chonkie import Tokenizer
from chonkie.tokenizer import CharacterTokenizer


logger = logging.getLogger(__name__)


DEFAULT_MODEL = "embeddinggemma-2:270m"
DEFAULT_BASE_URL = "http://localhost:11434"

DEFAULT_CHUNK_SIZE = 2400

DEFAULT_THRESHOLD = 0.85


class OllamaChonkieEmbeddings(BaseEmbeddings):

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
    ) -> None:

        if not model or not model.strip():
            raise ValueError("Ollama embedding model cannot be empty.")

        if not base_url or not base_url.strip():
            raise ValueError("Ollama base URL cannot be empty.")

        self.model = model
        self.base_url = base_url

        self.ollama = OllamaEmbeddings(
            model=self.model,
            base_url=self.base_url,
        )

        self._dimension: int | None = None

    def embed(self, text: str) -> list[float]:
        """Generate an embedding for a single text."""

        if not isinstance(text, str):
            raise TypeError("Embedding input must be a string.")

        if not text.strip():
            raise ValueError("Cannot generate an embedding for empty text.")

        vector = self.ollama.embed_query(text)

        if not vector:
            raise RuntimeError("Ollama returned an empty embedding.")

        self._validate_vector(vector)
        self._update_dimension(len(vector))

        return [float(value) for value in vector]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""

        if not isinstance(texts, list):
            raise TypeError("Embedding batch input must be a list.")

        if not texts:
            return []

        if any(not isinstance(text, str) or not text.strip() for text in texts):
            raise ValueError(
                "Every item in the embedding batch must be a non-empty string."
            )

        vectors = self.ollama.embed_documents(texts)

        if len(vectors) != len(texts):
            raise RuntimeError(
                "Ollama returned a different number of embeddings "
                "than the number of input texts."
            )

        if not vectors:
            return []

        dimension = len(vectors[0])

        for index, vector in enumerate(vectors):
            self._validate_vector(vector)

            if len(vector) != dimension:
                raise RuntimeError(
                    f"Inconsistent embedding dimensions in batch. "
                    f"Expected {dimension}, received {len(vector)} "
                    f"at index {index}."
                )

        self._update_dimension(dimension)

        return [
            [float(value) for value in vector]
            for vector in vectors
        ]

    def similarity(
        self,
        vector_a: list[float],
        vector_b: list[float],
    ) -> float:
        """Calculate cosine similarity between two embedding vectors."""

        if len(vector_a) != len(vector_b):
            raise ValueError(
                "Cannot calculate cosine similarity: "
                "embedding dimensions do not match."
            )

        if not vector_a:
            raise ValueError("Embedding vectors cannot be empty.")

        dot_product = sum(
            a * b for a, b in zip(vector_a, vector_b)
        )

        magnitude_a = math.sqrt(sum(value * value for value in vector_a))
        magnitude_b = math.sqrt(sum(value * value for value in vector_b))

        if magnitude_a == 0.0 or magnitude_b == 0.0:
            return 0.0

        similarity = dot_product / (magnitude_a * magnitude_b)

        # Protect against small floating-point rounding errors.
        return max(-1.0, min(1.0, similarity))

    @staticmethod
    def _count_characters(text: str) -> int:
        """
        Count characters rather than model tokens.

        This keeps the existing 2400-character chunk-size configuration
        meaningful. It is not a true tokenizer.
        """

        return len(text)

    def get_tokenizer_or_token_counter(self) -> Callable[[str], int]:
        """Return Chonkie's supported custom token-counter callable."""

        return self._count_characters

    @property
    def dimension(self) -> int:
        """
        Return the embedding dimension.

        If no embedding has been generated yet, probe Ollama once.
        """

        if self._dimension is None:
            self.embed("Embedding dimension probe.")

        if self._dimension is None:
            raise RuntimeError(
                "Unable to determine Ollama embedding dimension."
            )

        return self._dimension

    @staticmethod
    def _validate_vector(vector: list[float]) -> None:
        """Validate embedding values."""

        if not vector:
            raise ValueError("Embedding vector cannot be empty.")

        for value in vector:
            if not math.isfinite(float(value)):
                raise ValueError(
                    "Embedding vector contains a non-finite value."
                )

    def _update_dimension(self, dimension: int) -> None:
        """Ensure all embeddings use the same vector dimension."""

        if self._dimension is None:
            self._dimension = dimension
            return

        if self._dimension != dimension:
            raise RuntimeError(
                "Embedding dimension changed unexpectedly. "
                f"Expected {self._dimension}, received {dimension}."
            )

    def get_tokenizer(self):
        """Return a tokenizer compatible with Chonkie's BaseEmbeddings."""

        # return Tokenizer("character")
        return CharacterTokenizer()


def semantic_chunk_chonkie(
    text: str,
    metadata: dict[str, Any] | None = None,
    *,
    model: str = DEFAULT_MODEL,
    base_url: str = DEFAULT_BASE_URL,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    threshold: float = DEFAULT_THRESHOLD,
) -> list[Document]:
    """
    Split text into semantically related chunks using Chonkie.

    Args:
        text:
            Source document text.

        metadata:
            Optional metadata to attach to every LangChain Document.

        model:
            Ollama embedding model name.

        base_url:
            Ollama server URL.

        chunk_size:
            Target chunk size, measured in characters by this adapter.

        threshold:
            Semantic similarity percentile threshold (1-100).
            Higher values generally produce more conservative splitting.

    Returns:
        A list of LangChain Document objects.
    """

    if not isinstance(text, str):
        raise TypeError("Input text must be a string.")

    if not text.strip():
        logger.warning("Received empty text. Returning no chunks.")
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    # if not isinstance(threshold, int) or not 1 <= threshold <= 100:
    #     raise ValueError("threshold must be an integer between 1 and 100.")

    if (
        isinstance(threshold, bool)
        or not isinstance(threshold, (int, float))
        or not 0.0 <= threshold <= 1.0
    ):
        raise ValueError("threshold must be a number between 0 and 1.")

    source_metadata = dict(metadata or {})

    logger.info(
        "Starting Chonkie semantic chunking. "
        "Model=%s, chunk_size=%s characters, threshold=%s",
        model,
        chunk_size,
        threshold,
    )

    try:
        embeddings = OllamaChonkieEmbeddings(
            model=model,
            base_url=base_url,
        )

        chunker = SemanticChunker(
            embedding_model=embeddings,
            threshold=threshold,
            chunk_size=chunk_size,
            mode="window",
            similarity_window=1,
            min_sentences=1,
            min_chunk_size=2,
            min_characters_per_sentence=12,
        )

        chonkie_chunks = chunker.chunk(text)

        documents: list[Document] = []

        for index, chunk in enumerate(chonkie_chunks):
            chunk_text = getattr(chunk, "text", "")

            if not isinstance(chunk_text, str) or not chunk_text.strip():
                logger.warning(
                    "Skipping empty chunk at index %s.",
                    index,
                )
                continue

            chunk_metadata = {
                **source_metadata,
                "chunking_method": "chonkie_semantic",
                "chunk_index": index,
                "chunk_size": len(chunk_text),
                "token_count": getattr(chunk, "token_count", None),
                "start_index": getattr(chunk, "start_index", None),
                "end_index": getattr(chunk, "end_index", None),
            }

            # Remove metadata values that are None.
            chunk_metadata = {
                key: value
                for key, value in chunk_metadata.items()
                if value is not None
            }

            documents.append(
                Document(
                    page_content=chunk_text,
                    metadata=chunk_metadata,
                )
            )

        # logger.info("Chonkie generated %d chunks.", len(documents))

        print("\n" + "=" * 60)
        print(f"RESULTS: Generated {len(documents)} Semantic Chunks (Chonkie)")
        print("=" * 60)

        for idx, chunk in enumerate(documents, start=1):
            print(
                f"\n[Chunk {idx}] Character Length: {len(chunk.page_content)}")
            print("-" * 40)
            print(chunk.page_content.strip())
            print("-" * 40)

        return documents

    except Exception:
        logger.exception("Chonkie semantic chunking failed.")
        raise
