import numpy as np
from langchain_ollama import OllamaEmbeddings

import math

embeddings = OllamaEmbeddings(
    model="embeddinggemma-2:270m",
    base_url="http://localhost:11434",
)


def np_cosin(vector_1, vector_2):

    similarity = np.dot(
        vector_1,
        vector_2,
    ) / (
        np.linalg.norm(vector_1)
        * np.linalg.norm(vector_1)
    )

    distance = 1 - similarity
    print(f"Cosine Similarity: {similarity:.6f}")
    print(f"Cosine Distance:   {distance:.6f}")

    return {
        "distance": distance,
        "similarity": similarity
    }


# def sciket_cosin(vector_1, vector_2):
#     from sklearn.metrics.pairwise import cosine_similarity, cosine_distances

#     similarity = cosine_similarity(
#         [vector_1],
#         [vector_2],
#     )[0][0]

#     distance = cosine_distances(
#         [vector_1],
#         [vector_2],
#     )[0][0]

#     print(f"Cosine Similarity: {similarity:.6f}")
#     print(f"Cosine Distance:   {distance:.6f}")

#     return {
#         "distance": distance,
#         "similarity": similarity
#     }


def _cosine_distance(vector_a: list[float],
                     vector_b: list[float]):
    """Calculate cosine distance between two embeddings."""
    dot_product = sum(
        a * b for a, b in zip(vector_a, vector_b)
    )
    magnitude_a = math.sqrt(sum(a * a for a in vector_a))
    magnitude_b = math.sqrt(sum(b * b for b in vector_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 1.0
    similarity = dot_product / (magnitude_a * magnitude_b)

    distance = 1.0 - max(-1.0, min(1.0, similarity))

    return {
        "distance": distance,
        "similarity": similarity
    }


test_sentences = [
    "To create a new incident, open the ServiceNow Incident Management portal.",
    "Select the Create New option to initiate an incident request.",
    "To raise an incident, navigate to the ServiceNow incident portal.",
    "The change management process requires manager approval.",
    "The employee can request annual leave through the HR portal.",
]

vectors = embeddings.embed_documents(test_sentences)
result = {}

for i in range(len(test_sentences)):
    for j in range(i + 1, len(test_sentences)):

        result = _cosine_distance(
            vectors[i],
            vectors[j],
        )
        similarity = result["similarity"]  # type:ignore
        distance = result["distance"]  # type:ignore

        print(
            f"\nSentence {i + 1} vs Sentence {j + 1}"
            f"\nSimilarity: {similarity:.4f}"
            f"\nDistance:   {distance:.4f}"
        )
