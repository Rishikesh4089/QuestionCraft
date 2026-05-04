# app/rag/indexer/pipeline.py
"""
Index build pipeline.

Orchestrates: load → chunk → enrich → embed → FAISS index

This module is the only entry point for building a new index.
It is called by IndexStore when a cache miss occurs.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Tuple

import faiss
import numpy as np
from openai import AsyncOpenAI

from  app.core.config import Settings
from  app.rag.indexer.chunker import chunk_text, count_tokens
from  app.rag.indexer.embedder import Embedder
from  app.rag.indexer.enricher import enrich_chunks
from  app.rag.loaders.registry import load_document

logger = logging.getLogger(__name__)


async def build_index(
    file_paths: List[Path],
    settings: Settings,
    async_client: AsyncOpenAI,
) -> Tuple[faiss.Index, List[dict]]:
    """
    Full index build pipeline for a set of document files.

    Steps:
      1. Load each file → raw text (via registry, with OCR fallback)
      2. Chunk each document's text (token-aware)
      3. Enrich each chunk with topic/subtopic/content_type tags (async LLM)
      4. Embed all chunks in batches (sync OpenAI)
      5. Build and return a FAISS IndexFlatIP

    Args:
        file_paths: Absolute paths to the source documents.
        settings:   Application settings (keys, model names, etc.)
        async_client: Shared AsyncOpenAI client for enrichment calls.

    Returns:
        Tuple of (faiss_index, metadatas)
        metadatas is a list of dicts, one per chunk, aligned with the index vectors.

    Raises:
        IndexingError: If no text can be extracted from any file.
    """
    from  app.core.exceptions import IndexingError

    all_chunks: List[str] = []
    all_metadatas: List[dict] = []

    # ── 1 + 2: Load and chunk ─────────────────────────────────────────────
    for path in file_paths:
        try:
            text = load_document(path, enable_ocr=settings.ENABLE_OCR)
        except Exception as exc:
            logger.warning(f"Skipping {path.name}: {exc}")
            continue

        chunks = chunk_text(
            text,
            chunk_size=settings.CHUNK_SIZE_TOKENS,
            chunk_overlap=settings.CHUNK_OVERLAP_TOKENS,
        )

        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_metadatas.append({
                "doc_id": f"{path.stem}_{i}",
                "source": str(path),
                "filename": path.name,
                "chunk_index": i,
                "chunk_text": chunk,
                "token_count": count_tokens(chunk),
                # Enrichment fields — filled in step 3
                "topic": "",
                "subtopic": "",
                "content_type": "general",
            })

        logger.info(f"Loaded {path.name} → {len(chunks)} chunks")

    if not all_chunks:
        raise IndexingError(
            "No text could be extracted from the provided files.",
            detail="Check that files are readable and not empty or password-protected.",
        )

    # ── 3: Enrich ─────────────────────────────────────────────────────────
    if settings.ENRICH_CHUNKS:
        logger.info(f"Enriching {len(all_chunks)} chunks with topic metadata…")
        tags = await enrich_chunks(
            chunks=all_chunks,
            client=async_client,
            model=settings.ENRICHMENT_MODEL,
            concurrency=settings.ENRICHMENT_CONCURRENCY,
        )
        for meta, tag in zip(all_metadatas, tags):
            meta.update(tag)

    # ── 4: Embed ──────────────────────────────────────────────────────────
    logger.info(f"Embedding {len(all_chunks)} chunks…")
    embedder = Embedder(
        api_key=settings.OPENAI_API_KEY,
        model=settings.EMBEDDING_MODEL,
        embed_dim=settings.EMBEDDING_DIM,
        batch_size=settings.EMBED_BATCH_SIZE,
    )
    vectors: np.ndarray = embedder.embed(all_chunks)

    # ── 5: FAISS index ────────────────────────────────────────────────────
    dim = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)  # inner product on L2-normed vectors = cosine sim
    index.add(vectors)

    logger.info(f"Index built: {index.ntotal} vectors, dim={dim}")
    return index, all_metadatas