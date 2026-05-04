# app/rag/retriever/fusion.py
"""
Reciprocal Rank Fusion (RRF) for combining dense and sparse retrieval results.

RRF is robust to score scale differences between retrievers — it only uses
rank position, not raw scores, so dense cosine similarities and BM25 scores
can be combined directly without normalisation.

Reference: Cormack et al., "Reciprocal Rank Fusion outperforms Condorcet
and individual Rank Learning Methods" (SIGIR 2009)
"""
from __future__ import annotations

from typing import Dict, List, Tuple


def reciprocal_rank_fusion(
    dense_scores: Dict[int, List[float]],
    sparse_scores: Dict[int, float],
    top_k: int = 20,
    rrf_k: int = 60,
) -> List[Tuple[int, float]]:
    """
    Fuse dense multi-query scores and sparse BM25 scores via RRF.

    Algorithm:
      For each retriever, rank chunks by their score.
      Each chunk's RRF contribution = 1 / (rrf_k + rank).
      Chunks are ranked by the sum of their contributions across retrievers.

    Args:
        dense_scores:  {chunk_idx: [score_q1, score_q2, ...]} — one score
                       per query that retrieved this chunk.
        sparse_scores: {chunk_idx: best_bm25_score}
        top_k:         Number of fused results to return.
        rrf_k:         RRF smoothing constant (default 60 per the paper).

    Returns:
        List of (chunk_idx, rrf_score) sorted by descending rrf_score.
    """
    import numpy as np

    fused: Dict[int, float] = {}

    # ── Dense stream ─────────────────────────────────────────────────────
    # Average scores across queries so multi-query doesn't inflate scores
    # for chunks that happen to appear in many queries.
    dense_avg = {
        idx: float(np.mean(scores))
        for idx, scores in dense_scores.items()
    }
    for rank, (idx, _) in enumerate(
        sorted(dense_avg.items(), key=lambda x: x[1], reverse=True)
    ):
        fused[idx] = fused.get(idx, 0.0) + 1.0 / (rrf_k + rank + 1)

    # ── Sparse stream ─────────────────────────────────────────────────────
    for rank, (idx, _) in enumerate(
        sorted(sparse_scores.items(), key=lambda x: x[1], reverse=True)
    ):
        fused[idx] = fused.get(idx, 0.0) + 1.0 / (rrf_k + rank + 1)

    return sorted(fused.items(), key=lambda x: x[1], reverse=True)[:top_k]