# app/rag/retriever/reranker.py
"""
Reranker: Cohere cross-encoder reranking with RRF-order fallback.

Cohere reranking significantly improves precision by re-scoring candidates
using a cross-encoder model that considers (query, document) jointly.
When Cohere is unavailable or fails, candidates are returned in RRF order.
"""
from __future__ import annotations

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

try:
    import cohere  # type: ignore
    _HAS_COHERE = True
except ImportError:
    _HAS_COHERE = False
    logger.info(
        "cohere not installed — reranking will use RRF order. "
        "Run: pip install cohere"
    )


class Reranker:
    """
    Wraps Cohere async reranking.

    Usage:
        reranker = Reranker(api_key="...", model="rerank-english-v3.0")
        top = await reranker.rerank(query, candidates, top_n=4)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "rerank-english-v3.0",
    ) -> None:
        self._model = model
        self._client: Optional[object] = None

        if api_key and _HAS_COHERE:
            self._client = cohere.AsyncClient(api_key=api_key)  # type: ignore[attr-defined]
            logger.info(f"Cohere reranker initialised (model={model})")
        else:
            logger.info("Cohere reranker disabled — using RRF order.")

    @property
    def is_available(self) -> bool:
        return self._client is not None

    async def rerank(
        self,
        query: str,
        candidates: List[dict],
        top_n: int = 4,
    ) -> List[dict]:
        """
        Rerank candidates for *query*.

        Args:
            query:      The primary retrieval query string.
            candidates: List of dicts with at least a "text" key.
            top_n:      Number of results to return.

        Returns:
            Top *top_n* candidates sorted by relevance (best first).
        """
        if not candidates:
            return []

        if self._client is None or len(candidates) <= top_n:
            # No reranker or already few enough — just return top-n by RRF order
            return candidates[:top_n]

        try:
            docs = [c["text"] for c in candidates]
            result = await self._client.rerank(  # type: ignore[union-attr]
                model=self._model,
                query=query,
                documents=docs,
                top_n=top_n,
            )
            reranked = [candidates[r.index] for r in result.results]
            logger.debug(f"Cohere reranked {len(candidates)} → {len(reranked)} candidates")
            return reranked
        except Exception as exc:
            logger.warning(f"Cohere rerank failed, falling back to RRF order: {exc}")
            return candidates[:top_n]