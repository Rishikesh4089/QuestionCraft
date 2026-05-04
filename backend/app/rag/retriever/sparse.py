# app/rag/retriever/sparse.py
"""
Sparse BM25 retrieval.

BM25 is built from chunk texts at index-load time and kept in memory
alongside the FAISS index. It handles keyword-heavy queries that dense
retrieval can miss (exact formula names, acronyms, proper nouns).

Requires: pip install rank-bm25
"""
from __future__ import annotations

import logging
from typing import Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

try:
    from rank_bm25 import BM25Okapi  # type: ignore
    _HAS_BM25 = True
except ImportError:
    _HAS_BM25 = False
    logger.warning(
        "rank-bm25 not installed — sparse retrieval disabled. "
        "Run: pip install rank-bm25"
    )


def build_bm25(metadatas: List[dict]) -> Optional[object]:
    """
    Build a BM25Okapi corpus from chunk texts.

    Args:
        metadatas: List of chunk metadata dicts containing 'chunk_text'.

    Returns:
        BM25Okapi instance, or None if rank-bm25 is not installed.
    """
    if not _HAS_BM25:
        return None
    corpus = [m["chunk_text"].lower().split() for m in metadatas]
    return BM25Okapi(corpus)


def sparse_search(
    queries: List[str],
    bm25: object,
    k: int,
) -> Dict[int, float]:
    """
    Run BM25 search for each query and return best score per chunk.

    Args:
        queries: Raw query strings (tokenised internally)
        bm25:    BM25Okapi instance from build_bm25()
        k:       Number of top candidates to consider per query

    Returns:
        Dict mapping chunk_index → best BM25 score across all queries
    """
    if bm25 is None:
        return {}

    best_scores: Dict[int, float] = {}

    for query in queries:
        tokens = query.lower().split()
        scores: np.ndarray = bm25.get_scores(tokens)  # type: ignore[attr-defined]
        top_indices = np.argsort(scores)[::-1][:k]

        for idx in top_indices:
            idx = int(idx)
            score = float(scores[idx])
            if score > best_scores.get(idx, 0.0):
                best_scores[idx] = score

    return best_scores