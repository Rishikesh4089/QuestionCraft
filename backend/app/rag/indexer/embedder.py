# app/rag/indexer/embedder.py
"""
Batched text embedder using the OpenAI Embeddings API.

Returns L2-normalised float32 numpy arrays for use with FAISS IndexFlatIP
(inner product on unit vectors == cosine similarity).
"""
from __future__ import annotations

import logging
from typing import List

import numpy as np
from openai import OpenAI

from  app.core.exceptions import EmbeddingError

logger = logging.getLogger(__name__)

_EMBED_DIM_DEFAULTS = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}


class Embedder:
    """
    Wraps the synchronous OpenAI Embeddings API with batching and L2 normalisation.

    The sync client is intentional: batch embedding jobs run in a single
    background task and don't benefit from async concurrency. Using the sync
    client avoids event-loop contention with the generation coroutines.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        embed_dim: int = 1536,
        batch_size: int = 64,
    ) -> None:
        self._client = OpenAI(api_key=api_key)
        self.model = model
        self.embed_dim = embed_dim
        self.batch_size = batch_size

    def embed(self, texts: List[str]) -> np.ndarray:
        """
        Embed a list of strings.

        Returns:
            np.ndarray of shape (len(texts), embed_dim), dtype float32, L2-normalised.

        Raises:
            EmbeddingError: On API failure or dimension mismatch.
        """
        if not texts:
            return np.zeros((0, self.embed_dim), dtype="float32")

        all_vectors: list[list[float]] = []

        for batch_start in range(0, len(texts), self.batch_size):
            batch = texts[batch_start : batch_start + self.batch_size]
            try:
                response = self._client.embeddings.create(input=batch, model=self.model)
                all_vectors.extend(r.embedding for r in response.data)
            except Exception as exc:
                raise EmbeddingError(
                    f"Embedding batch {batch_start // self.batch_size + 1} failed",
                    detail=str(exc),
                    context={"model": self.model, "batch_size": len(batch)},
                ) from exc

        arr = np.array(all_vectors, dtype="float32")

        if arr.shape[1] != self.embed_dim:
            raise EmbeddingError(
                f"Embedding dimension mismatch: expected {self.embed_dim}, got {arr.shape[1]}",
                context={"model": self.model},
            )

        # L2-normalise so inner product == cosine similarity
        import faiss
        faiss.normalize_L2(arr)
        return arr