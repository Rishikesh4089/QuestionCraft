# app/rag/store.py
"""
IndexStore — manages the lifecycle of FAISS indexes.

Responsibilities:
  - Hash-based cache keying (SHA256 of file contents, order-independent)
  - Two-level cache: in-process memory (fast) → disk (persistent across restarts)
  - Atomic disk writes (write to tmp, then rename) to avoid corruption
  - BM25 reconstruction from metadata after disk load

Each unique set of syllabus files gets its own index directory:
  {RAG_INDEX_DIR}/{composite_hash}/faiss.index
  {RAG_INDEX_DIR}/{composite_hash}/meta.pkl
"""
from __future__ import annotations

import hashlib
import logging
import pickle
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import faiss

logger = logging.getLogger(__name__)


@dataclass
class IndexEntry:
    faiss_index: faiss.Index
    metadatas: List[dict]
    bm25: Optional[object]   # BM25Okapi or None


class IndexStore:
    """
    Thread-safe (GIL-protected) two-level cache for FAISS indexes.

    The in-process cache (dict) means the same index is never loaded from
    disk twice within a server process lifetime.
    """

    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir
        self._base_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, IndexEntry] = {}

    # ── Hashing ───────────────────────────────────────────────────────────

    @staticmethod
    def file_hash(path: Path) -> str:
        """SHA256 of file bytes."""
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for block in iter(lambda: f.read(65_536), b""):
                h.update(block)
        return h.hexdigest()

    @classmethod
    def composite_hash(cls, paths: List[Path]) -> str:
        """
        Order-independent composite hash for a set of files.
        Sorting individual hashes before combining means the same files
        in any upload order produce the same index key.
        """
        individual = sorted(cls.file_hash(p) for p in paths)
        combined = "|".join(individual)
        return hashlib.sha256(combined.encode()).hexdigest()[:24]

    # ── Public API ────────────────────────────────────────────────────────

    def exists(self, key: str) -> bool:
        """Return True if the index for *key* is available (memory or disk)."""
        if key in self._cache:
            return True
        return self._index_path(key).exists() and self._meta_path(key).exists()

    def get(self, key: str) -> Optional[IndexEntry]:
        """
        Retrieve an IndexEntry from the two-level cache.
        Returns None if not found (caller must build).
        """
        # L1: in-process memory
        if key in self._cache:
            logger.debug(f"Index cache hit (memory): {key}")
            return self._cache[key]

        # L2: disk
        idx_path = self._index_path(key)
        meta_path = self._meta_path(key)
        if idx_path.exists() and meta_path.exists():
            logger.info(f"Index cache hit (disk): {key}")
            return self._load_from_disk(key, idx_path, meta_path)

        return None

    def put(self, key: str, index: faiss.Index, metadatas: List[dict]) -> IndexEntry:
        """
        Persist an index to disk and register it in the memory cache.

        Disk write is atomic: data goes to a temp file first, then renamed.
        """
        idx_dir = self._index_dir(key)
        idx_dir.mkdir(parents=True, exist_ok=True)

        # Atomic FAISS write
        tmp_faiss = idx_dir / "faiss.index.tmp"
        faiss.write_index(index, str(tmp_faiss))
        tmp_faiss.rename(self._index_path(key))

        # Atomic metadata write
        tmp_meta = idx_dir / "meta.pkl.tmp"
        with open(tmp_meta, "wb") as f:
            pickle.dump(metadatas, f, protocol=pickle.HIGHEST_PROTOCOL)
        tmp_meta.rename(self._meta_path(key))

        bm25 = self._build_bm25(metadatas)
        entry = IndexEntry(faiss_index=index, metadatas=metadatas, bm25=bm25)
        self._cache[key] = entry

        logger.info(
            f"Index persisted: key={key}, chunks={len(metadatas)}, "
            f"vectors={index.ntotal}"
        )
        return entry

    def evict(self, key: str) -> None:
        """Remove an index from the memory cache (disk copy is kept)."""
        self._cache.pop(key, None)

    def clear_memory(self) -> None:
        """Evict all in-process index entries (disk copies are kept)."""
        self._cache.clear()

    # ── Private ───────────────────────────────────────────────────────────

    def _index_dir(self, key: str) -> Path:
        return self._base_dir / key

    def _index_path(self, key: str) -> Path:
        return self._index_dir(key) / "faiss.index"

    def _meta_path(self, key: str) -> Path:
        return self._index_dir(key) / "meta.pkl"

    def _load_from_disk(self, key: str, idx_path: Path, meta_path: Path) -> IndexEntry:
        faiss_index = faiss.read_index(str(idx_path))
        with open(meta_path, "rb") as f:
            metadatas: List[dict] = pickle.load(f)
        bm25 = self._build_bm25(metadatas)
        entry = IndexEntry(faiss_index=faiss_index, metadatas=metadatas, bm25=bm25)
        self._cache[key] = entry
        return entry

    @staticmethod
    def _build_bm25(metadatas: List[dict]) -> Optional[object]:
        try:
            from rank_bm25 import BM25Okapi  # type: ignore
            corpus = [m["chunk_text"].lower().split() for m in metadatas]
            return BM25Okapi(corpus)
        except ImportError:
            return None