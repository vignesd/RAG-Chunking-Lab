from src.rag_chunking_lab.chunkers import semantic_chonkie, semantic_llamaindex
from pathlib import Path

file_path = Path(
    r"C:\Vignesh\AgenticAI\Capstone Projects\RAG\RAG-Chunking-Lab\data\examples\semantic_short.txt")


text = file_path.read_text(encoding="utf-8")
chonkie = semantic_chonkie.semantic_chunk_chonkie(text)

for i in chonkie:
    print(i.page_content)
