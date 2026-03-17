import os
import requests
from fastapi import HTTPException

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
COHERE_API_URL = "https://api.cohere.com/v2/embed"


def get_embedding(text: str, input_type: str = "search_document") -> list:
    if not COHERE_API_KEY:
        raise RuntimeError("COHERE_API_KEY environment variable not set")

    response = requests.post(
        COHERE_API_URL,
        headers={
            "Authorization": f"Bearer {COHERE_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "texts": [text],
            "model": "embed-english-light-v3.0",
            "input_type": input_type,
            "embedding_types": ["float"]
        },
        timeout=30
    )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Cohere API error: {response.text}")

    return response.json()["embeddings"]["float"][0]


def get_embeddings_batch(texts: list, input_type: str = "search_document") -> list:
    if not COHERE_API_KEY:
        raise RuntimeError("COHERE_API_KEY environment variable not set")

    response = requests.post(
        COHERE_API_URL,
        headers={
            "Authorization": f"Bearer {COHERE_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "texts": texts,
            "model": "embed-english-light-v3.0",
            "input_type": input_type,
            "embedding_types": ["float"]
        },
        timeout=30
    )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Cohere API error: {response.text}")

    embeddings = response.json()["embeddings"]["float"]

    for emb in embeddings:
        if len(emb) != 384:
            raise RuntimeError(f"Expected 384 dimensions, got {len(emb)}")

    return embeddings

