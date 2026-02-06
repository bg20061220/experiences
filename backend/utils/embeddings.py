import os
import cohere

COHERE_API_KEY = os.getenv("COHERE_API_KEY")

co = cohere.Client(COHERE_API_KEY) if COHERE_API_KEY else None


def get_embedding(text: str, input_type: str = "search_document") -> list:
    """Generate embedding vector for the given text using Cohere API."""
    if not co:
        raise RuntimeError("COHERE_API_KEY environment variable not set")

    response = co.embed(
        texts=[text],
        model="embed-english-light-v3.0",
        input_type=input_type,
        embedding_types=["float"]
    )

    embedding = response.embeddings.float[0]

    if len(embedding) != 384:
        raise RuntimeError(f"Expected 384 dimensions, got {len(embedding)}")

    return embedding
