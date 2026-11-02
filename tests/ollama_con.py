from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(
    model="embeddinggemma-2:270m",
    # base_url="http://localhost:11434",
)

query_vector = embeddings.embed_query(
    "How do I raise a ServiceNow incident?"
)

print("Dimensions:", len(query_vector))
