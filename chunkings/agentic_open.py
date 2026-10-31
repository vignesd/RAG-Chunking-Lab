# agentic.py (Updated initialization section)
import os
from typing import Any
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.runnables import Runnable
from langchain_core.documents import Document
from logger_config import get_logger

logger = get_logger(__name__)


class BoundaryDecision(BaseModel):
    should_split: bool = Field(
        description="True if a semantic topic shift has occurred and a split should happen right here. False if the text continues the same topic."
    )
    reason: str = Field(
        description="Brief explanation for why a split is or isn't recommended.")


def agentic_chunk_open(text: str) -> list[Document]:
    logger.info("Starting Agentic Chunking execution...")

    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable is missing.")
        raise ValueError("OPENAI_API_KEY is required for agentic chunking.")

    logger.info(
        "Initializing ChatOpenAI model (gpt-4o-mini) for agent reasoning...")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Explicitly annotate and silence the generic type-checker mismatch
    structured_llm: Runnable[Any, BoundaryDecision] = llm.with_structured_output(
        BoundaryDecision)  # type: ignore[assignment]

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        logger.warning("No valid paragraphs found in the provided text.")
        return []

    logger.info(
        f"Loaded {len(paragraphs)} paragraphs for agentic boundary evaluation.")

    raw_chunks = []
    current_chunk_paragraphs = [paragraphs[0]]

    for i in range(1, len(paragraphs)):
        current_context = "\n\n".join(current_chunk_paragraphs)
        next_paragraph = paragraphs[i]

        prompt = f"""
You are an expert document chunking assistant for a RAG pipeline. 
Analyze the current accumulated chunk and the incoming paragraph. Determine if the incoming paragraph represents a distinct semantic topic shift that warrants a split.

Current Accumulated Chunk:
---
{current_context}
---

Incoming Paragraph:
---
{next_paragraph}
---
"""
        logger.info(f"Evaluating boundary after paragraph {i}...")
        decision: BoundaryDecision = structured_llm.invoke(prompt)

        logger.info(
            f"Agent Decision -> Split: {decision.should_split} | Reason: {decision.reason}")

        if decision.should_split:
            raw_chunks.append("\n\n".join(current_chunk_paragraphs))
            current_chunk_paragraphs = [next_paragraph]
        else:
            current_chunk_paragraphs.append(next_paragraph)

    if current_chunk_paragraphs:
        raw_chunks.append("\n\n".join(current_chunk_paragraphs))

    documents = [
        Document(
            page_content=chunk,
            metadata={"chunk_index": idx, "total_chunks": len(
                raw_chunks), "strategy": "agentic"}
        )
        for idx, chunk in enumerate(raw_chunks, start=1)
    ]

    logger.info(
        f"Successfully generated {len(documents)} agentic semantic chunks.")
    print("\n" + "=" * 60)
    print(f"RESULTS: Generated {len(documents)} Agentic Chunks")
    print("=" * 60)

    for idx, chunk in enumerate(documents, start=1):
        print(f"\n[Agentic Chunk {idx}] Length: {len(chunk.page_content)}")
        print("-" * 40)
        print(chunk.page_content.strip())
        print("-" * 40)
    return documents
