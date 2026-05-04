# agents/rag_pipeline.py
import os
import json
import asyncio
import hashlib
import pickle
import logging
from pathlib import Path
from typing import List, Optional, Dict, Tuple, Any
import faiss
import numpy as np
import tiktoken
from openai import AsyncOpenAI, OpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Try importing optional dependencies
# ─────────────────────────────────────────────
try:
    from rank_bm25 import BM25Okapi
    HAS_BM25 = True
except ImportError:
    HAS_BM25 = False
    logger.warning("rank_bm25 not installed — BM25 hybrid retrieval disabled. pip install rank-bm25")

try:
    import cohere
    HAS_COHERE = True
except ImportError:
    HAS_COHERE = False
    logger.warning("cohere not installed — reranking will use RRF scores only. pip install cohere")


# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
CHUNK_SIZE_TOKENS = 400          # tokens per chunk (not characters)
CHUNK_OVERLAP_TOKENS = 60        # overlap in tokens
MAX_CONTEXT_TOKENS = 2000        # max tokens sent to LLM per question
DEFAULT_TOP_K = 10               # retrieve top-k before reranking
RERANK_TOP_N = 4                 # keep top-n after reranking
EMBED_BATCH_SIZE = 64
EMBED_MODEL = "text-embedding-3-small"
EMBED_DIM = 1536                 # text-embedding-3-small dimension


# ─────────────────────────────────────────────
# Utility: token counting
# ─────────────────────────────────────────────
_enc = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    return len(_enc.encode(text))

def token_length_fn(text: str) -> int:
    return count_tokens(text)


# ─────────────────────────────────────────────
# Utility: file hashing
# ─────────────────────────────────────────────
def hash_file(path: str) -> str:
    """SHA256 of file content."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def composite_hash(file_paths: List[str]) -> str:
    """Deterministic composite hash for a set of files (order-independent)."""
    individual = sorted(hash_file(p) for p in file_paths)
    combined = "|".join(individual)
    return hashlib.sha256(combined.encode()).hexdigest()[:20]


# ─────────────────────────────────────────────
# Chunk metadata enrichment (async, cheap LLM)
# ─────────────────────────────────────────────
_ENRICH_PROMPT = """
Analyze this syllabus excerpt and return JSON ONLY:
{{
  "topic": "<main topic in 3-5 words>",
  "subtopic": "<specific subtopic in 3-5 words>",
  "content_type": "<one of: definition|theory|example|formula|procedure|overview>"
}}

Text:
{text}
"""

async def enrich_chunk_metadata(
    chunk_text: str,
    async_openai_client: AsyncOpenAI,
    model: str = "gpt-4o-mini"
) -> Dict[str, str]:
    """
    Uses a cheap LLM call to tag each chunk with topic/subtopic/content_type.
    Falls back to empty strings on failure — enrichment is best-effort.
    """
    try:
        resp = await async_openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": _ENRICH_PROMPT.format(text=chunk_text[:600])}],
            response_format={"type": "json_object"},
            max_tokens=80,
            temperature=0.0,
        )
        data = json.loads(resp.choices[0].message.content)
        return {
            "topic": data.get("topic", ""),
            "subtopic": data.get("subtopic", ""),
            "content_type": data.get("content_type", "general"),
        }
    except Exception as e:
        logger.debug(f"Chunk enrichment failed (non-critical): {e}")
        return {"topic": "", "subtopic": "", "content_type": "general"}


# ─────────────────────────────────────────────
# Core RAG Pipeline
# ─────────────────────────────────────────────
class RAGPipeline:
    """
    Hash-cached, hybrid-retrieval RAG pipeline.

    Usage:
        pipeline = RAGPipeline(base_index_dir="./indexes", openai_api_key="...")
        await pipeline.ensure_indexed(file_paths)
        results = await pipeline.multi_query_retrieve(queries=["...", "...", "..."])
    """

    def __init__(
        self,
        base_index_dir: str,
        openai_api_key: str,
        embedding_model: str = EMBED_MODEL,
        cohere_api_key: Optional[str] = None,
        enrich_chunks: bool = True,
        enrichment_model: str = "gpt-4o-mini",
    ):
        self.base_index_dir = Path(base_index_dir)
        self.base_index_dir.mkdir(parents=True, exist_ok=True)

        self.embedding_model = embedding_model
        self.enrich_chunks = enrich_chunks
        self.enrichment_model = enrichment_model

        # OpenAI clients (sync for embedding batches, async for enrichment)
        self._sync_client = OpenAI(api_key=openai_api_key)
        self._async_client = AsyncOpenAI(api_key=openai_api_key)

        # Cohere reranker (optional)
        self._cohere: Optional[Any] = None
        if HAS_COHERE and cohere_api_key:
            self._cohere = cohere.AsyncClient(api_key=cohere_api_key)

        # In-process index cache: hash → (faiss_index, metadatas, bm25)
        self._cache: Dict[str, Tuple[faiss.Index, List[dict], Optional[Any]]] = {}

        # Active index (set after ensure_indexed)
        self._active_hash: Optional[str] = None

    # ──────────────────────────────────────────
    # Public: index management
    # ──────────────────────────────────────────

    async def ensure_indexed(
        self,
        file_paths: List[str],
        force_reindex: bool = False,
    ) -> str:
        """
        Ensures files are indexed. Returns the composite hash.
        - If hash exists in memory cache: immediate return
        - If hash exists on disk: load from disk
        - Otherwise: build, enrich, and persist
        """
        c_hash = composite_hash(file_paths)
        self._active_hash = c_hash

        if not force_reindex and c_hash in self._cache:
            logger.info(f"✅ Index cache hit (memory): {c_hash}")
            return c_hash

        index_dir = self.base_index_dir / c_hash
        faiss_path = index_dir / "faiss.index"
        meta_path = index_dir / "meta.pkl"

        if not force_reindex and faiss_path.exists() and meta_path.exists():
            logger.info(f"✅ Index cache hit (disk): {c_hash}")
            faiss_index = faiss.read_index(str(faiss_path))
            with open(meta_path, "rb") as f:
                metadatas = pickle.load(f)
            bm25 = self._build_bm25(metadatas) if HAS_BM25 else None
            self._cache[c_hash] = (faiss_index, metadatas, bm25)
            return c_hash

        # Build index
        logger.info(f"🔨 Building new index: {c_hash}")
        index_dir.mkdir(parents=True, exist_ok=True)
        faiss_index, metadatas = await self._build_index(file_paths)
        bm25 = self._build_bm25(metadatas) if HAS_BM25 else None

        # Persist
        faiss.write_index(faiss_index, str(faiss_path))
        with open(meta_path, "wb") as f:
            pickle.dump(metadatas, f)

        self._cache[c_hash] = (faiss_index, metadatas, bm25)
        logger.info(f"✅ Index built and cached: {c_hash} ({len(metadatas)} chunks)")
        return c_hash

    # ──────────────────────────────────────────
    # Public: retrieval
    # ──────────────────────────────────────────

    async def multi_query_retrieve(
        self,
        queries: List[str],
        k: int = DEFAULT_TOP_K,
        rerank_top_n: int = RERANK_TOP_N,
        max_context_tokens: int = MAX_CONTEXT_TOKENS,
        index_hash: Optional[str] = None,
    ) -> List[dict]:
        """
        Multi-query hybrid retrieval with optional reranking.

        Args:
            queries: List of 1-5 query strings (generate variants upstream)
            k: Candidates per query before fusion
            rerank_top_n: Final chunks to return after reranking
            max_context_tokens: Hard token budget for returned chunks
            index_hash: Specify which cached index to use (defaults to active)

        Returns:
            List of dicts: [{text, meta, score}], token-limited
        """
        c_hash = index_hash or self._active_hash
        if c_hash not in self._cache:
            raise RuntimeError("No index loaded. Call ensure_indexed() first.")

        faiss_index, metadatas, bm25 = self._cache[c_hash]

        # Step 1: Embed all queries in one batch
        query_embeddings = self._embed_texts(queries)  # (n_queries, dim)

        # Step 2: Dense retrieval for each query
        all_dense_scores: Dict[int, List[float]] = {}
        for q_emb in query_embeddings:
            q_emb_2d = q_emb.reshape(1, -1)
            D, I = faiss_index.search(q_emb_2d, k)
            for score, idx in zip(D[0], I[0]):
                if idx < 0:
                    continue
                all_dense_scores.setdefault(int(idx), []).append(float(score))

        # Step 3: Sparse retrieval (BM25) for each query
        all_sparse_scores: Dict[int, float] = {}
        if bm25 is not None:
            for query in queries:
                scores = bm25.get_scores(query.lower().split())
                top_indices = np.argsort(scores)[::-1][:k]
                for idx in top_indices:
                    idx = int(idx)
                    all_sparse_scores[idx] = max(all_sparse_scores.get(idx, 0.0), float(scores[idx]))

        # Step 4: RRF fusion
        fused = self._reciprocal_rank_fusion(all_dense_scores, all_sparse_scores, top_k=k * 2)

        # Step 5: Build candidate list
        candidates = []
        for idx, rrf_score in fused:
            if idx >= len(metadatas):
                continue
            meta = metadatas[idx]
            candidates.append({
                "text": meta["chunk_text"],
                "meta": meta,
                "score": rrf_score,
                "idx": idx,
            })

        if not candidates:
            logger.warning("Retrieval returned 0 candidates.")
            return []

        # Step 6: Rerank (Cohere or fallback to RRF order)
        reranked = await self._rerank(queries[0], candidates, top_n=rerank_top_n)

        # Step 7: Token budget enforcement
        result = []
        used_tokens = 0
        for item in reranked:
            t = count_tokens(item["text"])
            if used_tokens + t > max_context_tokens:
                break
            result.append(item)
            used_tokens += t

        logger.info(f"📚 Retrieved {len(result)} chunks | {used_tokens} tokens | queries: {len(queries)}")
        return result

    def build_context_string(self, chunks: List[dict]) -> str:
        """Join retrieved chunks into a single context string."""
        parts = []
        for i, c in enumerate(chunks):
            topic_label = ""
            if c["meta"].get("topic"):
                topic_label = f"[Topic: {c['meta']['topic']}] "
            parts.append(f"{topic_label}{c['text']}")
        return "\n\n---\n\n".join(parts)

    # ──────────────────────────────────────────
    # Internal: index building
    # ──────────────────────────────────────────

    async def _build_index(
        self, file_paths: List[str]
    ) -> Tuple[faiss.Index, List[dict]]:
        """Extract text, chunk, enrich, embed, build FAISS index."""
        from agents.rag.loaders import load_document_from_path  

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE_TOKENS,
            chunk_overlap=CHUNK_OVERLAP_TOKENS,
            length_function=token_length_fn,
            separators=["\n\n\n", "\n\n", "\n", ". ", " "],
        )

        all_chunks: List[str] = []
        all_metadatas: List[dict] = []

        for path in file_paths:
            try:
                text = load_document_from_path(path)
            except Exception as e:
                logger.warning(f"Failed to load {path}: {e}")
                continue

            if not text.strip():
                continue

            chunks = splitter.split_text(text)
            stem = Path(path).stem

            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_metadatas.append({
                    "doc_id": f"{stem}_{i}",
                    "source": str(path),
                    "chunk_index": i,
                    "chunk_text": chunk,
                    "token_count": count_tokens(chunk),
                    # Enrichment fields — filled below
                    "topic": "",
                    "subtopic": "",
                    "content_type": "general",
                })

        if not all_chunks:
            raise ValueError("No text extracted from provided files.")

        # Enrich chunk metadata with topic tags (concurrent, best-effort)
        if self.enrich_chunks:
            logger.info(f"🏷️  Enriching {len(all_chunks)} chunks with topic metadata...")
            enrichment_tasks = [
                enrich_chunk_metadata(chunk, self._async_client, self.enrichment_model)
                for chunk in all_chunks
            ]
            # Batch to avoid overwhelming the API (20 concurrent max)
            enriched_tags = []
            batch_size = 20
            for i in range(0, len(enrichment_tasks), batch_size):
                batch_results = await asyncio.gather(
                    *enrichment_tasks[i:i + batch_size], return_exceptions=True
                )
                for r in batch_results:
                    if isinstance(r, Exception):
                        enriched_tags.append({"topic": "", "subtopic": "", "content_type": "general"})
                    else:
                        enriched_tags.append(r)

            for meta, tags in zip(all_metadatas, enriched_tags):
                meta.update(tags)

        # Embed
        logger.info(f"🔢 Embedding {len(all_chunks)} chunks...")
        vectors = self._embed_texts(all_chunks)  # (n, dim)

        # Build FAISS index
        d = vectors.shape[1]
        faiss_index = faiss.IndexFlatIP(d)
        faiss_index.add(vectors)

        return faiss_index, all_metadatas

    # ──────────────────────────────────────────
    # Internal: embedding
    # ──────────────────────────────────────────

    def _embed_texts(self, texts: List[str]) -> np.ndarray:
        """Batch embed texts. Returns (n, dim) float32 ndarray, L2-normalized."""
        if not texts:
            return np.zeros((0, EMBED_DIM), dtype="float32")

        all_embs = []
        for i in range(0, len(texts), EMBED_BATCH_SIZE):
            batch = texts[i:i + EMBED_BATCH_SIZE]
            response = self._sync_client.embeddings.create(
                input=batch,
                model=self.embedding_model,
            )
            all_embs.extend([r.embedding for r in response.data])

        arr = np.array(all_embs, dtype="float32")
        faiss.normalize_L2(arr)
        return arr

    # ──────────────────────────────────────────
    # Internal: BM25
    # ──────────────────────────────────────────

    def _build_bm25(self, metadatas: List[dict]) -> Optional[Any]:
        if not HAS_BM25:
            return None
        corpus = [m["chunk_text"].lower().split() for m in metadatas]
        return BM25Okapi(corpus)

    # ──────────────────────────────────────────
    # Internal: RRF fusion
    # ──────────────────────────────────────────

    def _reciprocal_rank_fusion(
        self,
        dense_scores: Dict[int, List[float]],
        sparse_scores: Dict[int, float],
        top_k: int = 20,
        rrf_k: int = 60,
    ) -> List[Tuple[int, float]]:
        """
        Fuse dense (multi-query) and sparse scores via Reciprocal Rank Fusion.
        dense_scores: {idx: [score_from_query1, score_from_query2, ...]}
        sparse_scores: {idx: best_bm25_score}
        """
        all_idx = set(dense_scores.keys()) | set(sparse_scores.keys())
        fused: Dict[int, float] = {}

        # Dense: average scores across queries, then rank
        dense_avg = {idx: np.mean(scores) for idx, scores in dense_scores.items()}
        for rank, idx in enumerate(sorted(dense_avg, key=dense_avg.get, reverse=True)):
            fused[idx] = fused.get(idx, 0.0) + 1.0 / (rrf_k + rank + 1)

        # Sparse: rank by BM25 score
        for rank, idx in enumerate(sorted(sparse_scores, key=sparse_scores.get, reverse=True)):
            if idx in all_idx:
                fused[idx] = fused.get(idx, 0.0) + 1.0 / (rrf_k + rank + 1)

        top = sorted(fused.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return top

    # ──────────────────────────────────────────
    # Internal: reranking
    # ──────────────────────────────────────────

    async def _rerank(
        self,
        query: str,
        candidates: List[dict],
        top_n: int = RERANK_TOP_N,
    ) -> List[dict]:
        """
        Rerank candidates. Uses Cohere if available, else returns top-n by RRF score.
        """
        if self._cohere and len(candidates) > top_n:
            try:
                docs = [c["text"] for c in candidates]
                result = await self._cohere.rerank(
                    model="rerank-english-v3.0",
                    query=query,
                    documents=docs,
                    top_n=top_n,
                )
                reranked = [candidates[r.index] for r in result.results]
                return reranked
            except Exception as e:
                logger.warning(f"Cohere rerank failed, falling back to RRF order: {e}")

        # Fallback: RRF order (already sorted by score)
        return candidates[:top_n]

    # ──────────────────────────────────────────
    # Utility
    # ──────────────────────────────────────────

    def index_exists(self, file_paths: List[str]) -> bool:
        c_hash = composite_hash(file_paths)
        if c_hash in self._cache:
            return True
        index_dir = self.base_index_dir / c_hash
        return (index_dir / "faiss.index").exists() and (index_dir / "meta.pkl").exists()

    def cleanup(self):
        """Release in-memory cache."""
        self._cache.clear()
        self._active_hash = None
