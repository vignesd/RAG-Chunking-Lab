
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from logger_config import get_logger

logger = get_logger(__name__)

if not os.getenv("OPENAI_API_KEY"):
    logger.error("OPENAI_API_KEY environment variable is required.")
    exit(1)

# Pydantic schema to enforce structured LLM responses for agentic split points


class SplitDecision(BaseModel):
    chunk_summary: str = Field(
        description="A concise summary of the logical segment.")
    should_split_after: bool = Field(
        description="True if a semantic topic shift occurs here, otherwise False.")


COMPLEX_TEXT_SECTION = (
    "In 2024, corporate automation strategies shifted toward hybrid cloud workflows. "
    "Companies integrated Python scripts with enterprise platforms. "
    "Meanwhile, global financial regulations underwent strict revisions regarding data privacy compliance."
)


def agentic_chunk(text: str = ""):
    logger.info("=== Starting Agentic Chunking Demo ===")
    if not text:
        text = COMPLEX_TEXT_SECTION

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.0,
    )
    structured_llm = llm.with_structured_output(SplitDecision)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert document layout agent. Evaluate if the given text segment represents a distinct standalone sub-topic requiring a chunk boundary split."),
        ("user", "Text segment: {text}")
    ])

    chain = prompt | structured_llm

    logger.info("Invoking LLM agent to analyze text boundaries...")
    result: SplitDecision = chain.invoke(
        {"text": text})  # type:ignore

    print("\n" + "=" * 50)
    print("AGENTIC CHUNKING ANALYSIS RESULTS")
    print("=" * 50)
    print(f"Analyzed Text: {text}")
    print(f"Segment Summary: {result.chunk_summary}")
    print(f"Recommended Boundary Split: {result.should_split_after}")
