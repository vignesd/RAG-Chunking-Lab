from collections.abc import Callable
from pathlib import Path

from .chunkers.agentic import agentic_chunk
from .chunkers.fixed_size import fixed_chunk
from .chunkers.markdown import document_chunk
from .chunkers.recursive import recursive_chunk
from .chunkers.semantic import semantic_chunk
from .logging_config import setup_logging


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_FILE = PROJECT_ROOT / "data" / "examples" / "sample_document.md"
STRATEGIES: dict[int, tuple[str, Callable[[str], object]]] = {
    1: ("Fixed Chunking", fixed_chunk),
    2: ("Recursive Chunking", recursive_chunk),
    3: ("Markdown-Aware Chunking", document_chunk),
    4: ("Semantic Chunking (OpenAI)", semantic_chunk),
    5: ("Agentic Chunking (OpenAI)", agentic_chunk),
}

MENU_PROMPT = """\
Choose a chunking strategy (1-5):
1. Fixed Chunking
2. Recursive Chunking
3. Markdown-Aware Chunking
4. Semantic Chunking (OpenAI)
5. Agentic Chunking (OpenAI)
"""


def prompt_for_option() -> int:
    """Prompt until the user enters a valid strategy number."""
    while True:
        try:
            option = int(input(MENU_PROMPT))
        except ValueError:
            print("Please enter a number from 1 to 5.")
            continue

        if option in STRATEGIES:
            return option

        print("Choose a strategy from 1 to 5.")


def main(option: int = 1) -> None:
    """Run the selected chunking strategy on the sample document."""
    try:
        strategy_name, chunker = STRATEGIES[option]
    except KeyError:
        raise ValueError("Choose a chunking strategy from 1 to 5.") from None

    setup_logging()
    sample_text = SAMPLE_FILE.read_text(encoding="utf-8")

    print("=" * 50)
    print("ORIGINAL TEXT")
    print("=" * 50)
    print(sample_text)
    print("=" * 50)
    print(f"Selected strategy: {strategy_name}")
    chunker(sample_text)


if __name__ == "__main__":
    main(prompt_for_option())
