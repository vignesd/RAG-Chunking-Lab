import re
import math

from langchain_ollama import OllamaEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_core.documents import Document
from ..logging_config import get_logger

logger = get_logger(__name__)

model_name = "embeddinggemma-2:270m"
embeddings = OllamaEmbeddings(
    model=model_name,
    base_url="http://localhost:11434",
)

# from langchain_openai import OpenAIEmbeddings
# embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences while retaining sentence content."""

    text = re.sub(r"[ \t]+", " ", text.strip())

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def _cosine_distance(vector_a: list[float],
                     vector_b: list[float]) -> float:
    """Calculate cosine distance between two embeddings."""

    dot_product = sum(
        a * b for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(sum(a * a for a in vector_a))
    magnitude_b = math.sqrt(sum(b * b for b in vector_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 1.0

    similarity = dot_product / (magnitude_a * magnitude_b)

    # Cosine distance = 1 - cosine similarity
    return 1.0 - max(-1.0, min(1.0, similarity))


def _calculate_percentile(
    values: list[float],
    percentile: float,
) -> float:
    """Calculate a percentile using linear interpolation."""

    if not values:
        return 1.0

    sorted_values = sorted(values)
    position = (len(sorted_values) - 1) * percentile / 100
    lower_index = math.floor(position)
    upper_index = math.ceil(position)

    if lower_index == upper_index:
        return sorted_values[lower_index]

    weight = position - lower_index

    return (
        sorted_values[lower_index] * (1 - weight)
        + sorted_values[upper_index] * weight
    )


def _group_semantic_units(
    units: list[str],
    embeddings: OllamaEmbeddings,
    breakpoint_percentile: float = 85,
    min_chunk_chars: int = 500,
    max_chunk_chars: int = 2400,
) -> list[str]:
    """
    Group sentences or paragraphs based on embedding distance.

    A significant increase in cosine distance indicates
    a possible semantic boundary.
    """

    if not units:
        return []

    if len(units) == 1:
        return units

    vectors = embeddings.embed_documents(units)

    distances = [
        _cosine_distance(vectors[i], vectors[i + 1])
        for i in range(len(vectors) - 1)
    ]

    threshold = _calculate_percentile(
        distances,
        breakpoint_percentile,
    )

    logger.info(
        "Semantic boundary threshold: %.4f",
        threshold,
    )

    groups: list[list[str]] = []
    boundaries: list[float] = []

    current_group = [units[0]]

    for index, unit in enumerate(units[1:]):
        distance = distances[index]

        current_length = sum(len(item) for item in current_group)
        new_length = current_length + len(unit)

        semantic_break = distance > threshold
        size_break = new_length > max_chunk_chars

        if semantic_break or size_break:
            groups.append(current_group)
            boundaries.append(distance)
            current_group = [unit]
        else:
            current_group.append(unit)

    groups.append(current_group)

    # Merge undersized groups with their most similar neighbor
    # where the combined size does not exceed max_chunk_chars.
    index = 0

    while index < len(groups):
        group_length = sum(len(item) for item in groups[index])

        if group_length >= min_chunk_chars or len(groups) == 1:
            index += 1
            continue

        merge_left = (
            index > 0
            and sum(len(item) for item in groups[index - 1])
            + group_length <= max_chunk_chars
        )

        merge_right = (
            index < len(groups) - 1
            and group_length
            + sum(len(item) for item in groups[index + 1])
            <= max_chunk_chars
        )

        if merge_left and merge_right:
            if boundaries[index - 1] <= boundaries[index]:
                groups[index - 1].extend(groups[index])
                groups.pop(index)
                boundaries.pop(index - 1)
                index = max(0, index - 1)
            else:
                groups[index].extend(groups[index + 1])
                groups.pop(index + 1)
                boundaries.pop(index)

        elif merge_left:
            groups[index - 1].extend(groups[index])
            groups.pop(index)
            boundaries.pop(index - 1)
            index = max(0, index - 1)

        elif merge_right:
            groups[index].extend(groups[index + 1])
            groups.pop(index + 1)
            boundaries.pop(index)

        else:
            index += 1

    return [
        "\n".join(group).strip()
        for group in groups
        if group
    ]


def semantic_chunk(text: str) -> list[Document]:
    """
    Splits text semantically using LangChain's native SemanticChunker 
    powered by OpenAI/Ollama embeddings and dynamic percentile breakpoints.
    """
    logger.info("Initializing LangChain SemanticChunker execution...")

    logger.info(
        f"Initializing OpenAI Embeddings model ({model_name})...")

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


def semantic_chunk_similarity(
    text: str,
    breakpoint_percentile: float = 85,
    min_chunk_chars: int = 500,
    max_chunk_chars: int = 2400,
) -> list[Document]:
    """
    Simple semantic chunking using consecutive sentence
    embedding similarity and cosine distance.

    Does not use LangChain SemanticChunker.
    """

    logger.info("Starting simple semantic chunking...")

    sentences = _split_sentences(text)

    logger.info("Extracted %d sentences.", len(sentences))

    chunks = _group_semantic_units(
        units=sentences,
        embeddings=embeddings,
        breakpoint_percentile=breakpoint_percentile,
        min_chunk_chars=min_chunk_chars,
        max_chunk_chars=max_chunk_chars,
    )

    documents = [
        Document(
            page_content=chunk,
            metadata={
                "chunking_method": "simple_semantic",
                "chunk_index": index,
            },
        )
        for index, chunk in enumerate(chunks)
    ]

    logger.info(
        "Simple semantic chunking completed. Generated %d chunks.",
        len(documents),
    )

    for index, document in enumerate(documents[:10], start=1):
        logger.info(
            "[Chunk %d] Character length: %d",
            index,
            len(document.page_content),
        )

        print(f"\n[Chunk {index}]")
        print("-" * 50)
        print(document.page_content)
        print("-" * 50)

    return documents


def semantic_chunk_hybrid(
    text: str,
    breakpoint_percentile: float = 85,
    min_chunk_chars: int = 500,
    max_chunk_chars: int = 2400,
) -> list[Document]:
    """
    Hybrid semantic and structural chunking.

    1. Detect Markdown headings.
    2. Divide the document into independent sections.
    3. Preserve section headings.
    4. Use paragraphs as semantic units.
    5. Split oversized paragraphs into sentences.
    6. Apply embedding-based semantic boundaries.

    Does not use LangChain SemanticChunker.
    """

    logger.info("Starting hybrid semantic + structural chunking...")

    # Detect Markdown headings and divide the document.
    heading_pattern = re.compile(
        r"^(#{1,6})\s+(.+?)\s*$",
        re.MULTILINE,
    )

    matches = list(heading_pattern.finditer(text))

    sections = []

    if not matches:
        sections.append({
            "heading": "",
            "content": text.strip(),
        })
    else:
        # Content before the first heading.
        if text[:matches[0].start()].strip():
            sections.append({
                "heading": "",
                "content": text[:matches[0].start()].strip(),
            })

        for index, match in enumerate(matches):
            next_start = (
                matches[index + 1].start()
                if index + 1 < len(matches)
                else len(text)
            )

            sections.append({
                "heading": match.group(0).strip(),
                "content": text[match.end():next_start].strip(),
            })

    logger.info("Detected %d document sections.", len(sections))

    documents: list[Document] = []
    chunk_index = 0

    for section_index, section in enumerate(sections):

        heading = section["heading"]
        content = section["content"]

        if not content:
            continue

        logger.info(
            "Processing section %d: %s",
            section_index + 1,
            heading or "No heading",
        )

        # Use paragraphs as semantic units.
        paragraphs = [
            paragraph.strip()
            for paragraph in re.split(r"\n\s*\n", content)
            if paragraph.strip()
        ]

        units = []

        for paragraph in paragraphs:

            if len(paragraph) > max_chunk_chars:
                # Split oversized paragraphs into sentences.
                units.extend(_split_sentences(paragraph))
            else:
                units.append(paragraph)

        if not units:
            continue

        # Semantic chunking happens within each section.
        section_chunks = _group_semantic_units(
            units=units,
            embeddings=embeddings,
            breakpoint_percentile=breakpoint_percentile,
            min_chunk_chars=min_chunk_chars,
            max_chunk_chars=max_chunk_chars,
        )

        for chunk in section_chunks:

            # Preserve the heading in every generated chunk.
            page_content = (
                f"{heading}\n\n{chunk}"
                if heading
                else chunk
            )

            documents.append(
                Document(
                    page_content=page_content,
                    metadata={
                        "chunking_method": "hybrid_semantic_structural",
                        "chunk_index": chunk_index,
                        "section_index": section_index,
                        "section_heading": heading,
                    },
                )
            )

            chunk_index += 1

    logger.info(
        "Hybrid semantic chunking completed. Generated %d chunks.",
        len(documents),
    )

    for index, document in enumerate(documents[:10], start=1):

        logger.info(
            "[Chunk %d] Character length: %d | Heading: %s",
            index,
            len(document.page_content),
            document.metadata.get("section_heading"),
        )

        print(f"\n[Chunk {index}]")
        print("-" * 50)
        print(document.page_content)
        print("-" * 50)

    return documents
