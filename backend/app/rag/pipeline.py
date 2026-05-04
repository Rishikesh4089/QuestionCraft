# app/rag/pipeline.py
"""
RAGPipeline — public façade for the entire RAG subsystem.

Callers (services, API handlers) only interact with this class.
All internal complexity (loading, chunking, embedding, indexing,
dense/sparse retrieval, fusion, reranking) is hidden behind two methods:

    await pipeline.ensure_indexed(file_paths)
    chunks = await pipeline.retrieve(queries, index_key)
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

from openai import AsyncOpenAI

from  app.core.config import Settings
from  app.core.exceptions import IndexNotFoundError, RetrievalError
from  app.rag.indexer.embedder import Embedder
from  app.rag.indexer.pipeline import build_index
from  app.rag.retriever.dense import dense_search
from  app.rag.retriever.sparse import sparse_search
from  app.rag.retriever.fusion import reciprocal_rank_fusion
from  app.rag.retriever.reranker import Reranker
from  app.rag.store import IndexStore

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Application-scoped singleton.

    Instantiated once during FastAPI lifespan startup and injected into
    request handlers via FastAPI dependency injection.

    Args:
        settings:      Application settings.
        async_client:  Shared AsyncOpenAI client (for enrichment).
    """

    def __init__(self, settings: Settings, async_client: AsyncOpenAI) -> None:
        self._settings = settings
        self._async_client = async_client
        self._store = IndexStore(base_dir=Path(settings.RAG_INDEX_DIR))
        self._embedder = Embedder(
            api_key=settings.OPENAI_API_KEY,
            model=settings.EMBEDDING_MODEL,
            embed_dim=settings.EMBEDDING_DIM,
            batch_size=settings.EMBED_BATCH_SIZE,
        )
        self._reranker = Reranker(
            api_key=settings.COHERE_API_KEY,
            model=settings.COHERE_RERANK_MODEL,
        )

    # ── Public: Indexing ─────────────────────────────────────────────────

    async def ensure_indexed(
        self,
        file_paths: List[Path],
        force_rebuild: bool = False,
    ) -> str:
        """
        Ensure the given files are indexed. Returns the index key (hash).

        Cache behaviour:
          - Memory hit  → immediate return (zero I/O)
          - Disk hit    → load from disk into memory, return
          - Miss        → build full index, persist to disk, cache in memory

        Args:
            file_paths:    Absolute paths to syllabus documents.
            force_rebuild: Ignore all caches and rebuild from scratch.

        Returns:
            index_key: The composite hash string identifying this index.
        """
        key = self._store.composite_hash(file_paths)

        if not force_rebuild:
            entry = self._store.get(key)
            if entry is not None:
                logger.info(f"Index ready (cached): key={key}")
                return key

        logger.info(f"Building new index: key={key}, files={len(file_paths)}")
        faiss_index, metadatas = await build_index(
            file_paths=file_paths,
            settings=self._settings,
            async_client=self._async_client,
        )
        self._store.put(key, faiss_index, metadatas)
        return key

    def index_exists(self, file_paths: List[Path]) -> bool:
        """Check whether an index for these files already exists (memory or disk)."""
        key = self._store.composite_hash(file_paths)
        return self._store.exists(key)

    def composite_hash(self, file_paths: List[Path]) -> str:
        return self._store.composite_hash(file_paths)

    # ── Public: Retrieval ────────────────────────────────────────────────

    async def retrieve(
        self,
        queries: List[str],
        index_key: str,
        top_k: int = 10,
        rerank_top_n: int = 4,
        max_context_tokens: int = 2000,
    ) -> List[dict]:
        """
        Multi-query hybrid retrieval with optional Cohere reranking.

        Pipeline:
          1. Embed all queries in one batch
          2. Dense FAISS search per query → aggregate scores
          3. Sparse BM25 search per query → best score per chunk
          4. RRF fusion of dense + sparse
          5. Cohere reranking (or RRF order fallback)
          6. Token budget enforcement

        Args:
            queries:           1–5 query strings for the same question slot.
            index_key:         Hash key from ensure_indexed().
            top_k:             Candidates to retrieve before reranking.
            rerank_top_n:      Final chunks to keep after reranking.
            max_context_tokens: Hard token ceiling on total returned text.

        Returns:
            List of chunk dicts: [{text, meta, score}]

        Raises:
            IndexNotFoundError: If index_key is not in any cache.
            RetrievalError:     On unexpected retrieval failure.
        """
        entry = self._store.get(index_key)
        if entry is None:
            raise IndexNotFoundError(
                f"Index '{index_key}' not found. Call ensure_indexed() first."
            )

        try:
            # 1. Embed queries
            query_vectors = self._embedder.embed(queries)

            # 2. Dense search
            dense_scores = dense_search(query_vectors, entry.faiss_index, k=top_k)

            # 3. Sparse search
            sparse_scores = sparse_search(queries, entry.bm25, k=top_k) if entry.bm25 else {}

            # 4. RRF fusion
            fused = reciprocal_rank_fusion(
                dense_scores=dense_scores,
                sparse_scores=sparse_scores,
                top_k=top_k * 2,
            )

            # 5. Build candidate list
            candidates: List[dict] = []
            for chunk_idx, rrf_score in fused:
                if chunk_idx >= len(entry.metadatas):
                    continue
                meta = entry.metadatas[chunk_idx]
                candidates.append({
                    "text": meta["chunk_text"],
                    "meta": meta,
                    "score": rrf_score,
                })

            if not candidates:
                logger.warning(f"Retrieval returned 0 candidates for key={index_key}")
                return []

            # 6. Rerank
            reranked = await self._reranker.rerank(
                query=queries[0],
                candidates=candidates,
                top_n=rerank_top_n,
            )

            # 7. Token budget
            from  app.rag.indexer.chunker import count_tokens
            result: List[dict] = []
            used_tokens = 0
            for item in reranked:
                t = count_tokens(item["text"])
                if used_tokens + t > max_context_tokens:
                    break
                result.append(item)
                used_tokens += t

            logger.info(
                f"Retrieved {len(result)} chunks | {used_tokens} tokens | "
                f"{len(queries)} queries | key={index_key}"
            )
            return result

        except IndexNotFoundError:
            raise
        except Exception as exc:
            raise RetrievalError(
                "Retrieval failed unexpectedly",
                detail=str(exc),
                context={"index_key": index_key, "query_count": len(queries)},
            ) from exc

    # ── Public: Context building ─────────────────────────────────────────

    @staticmethod
    def build_context(chunks: List[dict]) -> str:
        """
        Format retrieved chunks into a single context string for the LLM.
        Includes topic label when available.
        """
        parts: List[str] = []
        for chunk in chunks:
            topic = chunk["meta"].get("topic", "")
            prefix = f"[Topic: {topic}] " if topic else ""
            parts.append(f"{prefix}{chunk['text']}")
        return "\n\n---\n\n".join(parts)