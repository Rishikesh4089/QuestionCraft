# app/rag/retriever/dense.py
"""
Dense vector retrieval using FAISS IndexFlatIP.

Takes pre-embedded query vectors and returns ranked (index, score) pairs.
"""
from __future__ import annotations

import logging
from typing import Dict, List

import faiss
import numpy as np

logger = logging.getLogger(__name__)


def dense_search(
    query_vectors: np.ndarray,
    index: faiss.Index,
    k: int,
) -> Dict[int, List[float]]:
    """
    Run FAISS search for each query vector and collect per-chunk scores.

    Args:
        query_vectors: shape (n_queries, dim), L2-normalised float32
        index:         FAISS index to search
        k:             Top-k results per query

    Returns:
        Dict mapping chunk_index → list of cosine similarity scores
        (one score per query that retrieved this chunk)
    """
    results: Dict[int, List[float]] = {}

    for i in range(query_vectors.shape[0]):
        q = query_vectors[i : i + 1]  # shape (1, dim)
        distances, indices = index.search(q, k)

        for score, idx in zip(distances[0], indices[0]):
            if idx < 0:
                continue  # FAISS pads with -1 when fewer than k results exist
            results.setdefault(int(idx), []).append(float(score))

    return results