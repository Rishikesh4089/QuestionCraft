# agents/rag_pipeline.py
import os
import faiss
import numpy as np
import hashlib
import pickle
from typing import List, Optional
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
import tiktoken


class RAGPipeline:
    """
    FAISS-backed RAG pipeline for syllabus/question generation.
    - Uses OpenAI embedding model (default: text-embedding-3-small)
    - Splits large documents into manageable chunks
    - Persists FAISS index + metadata
    - Handles token-safe retrieval
    """

    def __init__(
        self,
        index_dir: str,
        embedding_client: OpenAI,
        embedding_model: str = "text-embedding-3-small",
        chunk_size: int = 1000,
        chunk_overlap: int = 150,
        max_tokens_per_query: int = 20000,
    ):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.embedding_client = embedding_client
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_tokens_per_query = max_tokens_per_query

        self.index_path = self.index_dir / "faiss.index"
        self.meta_path = self.index_dir / "meta.pkl"

        self._faiss_index: Optional[faiss.IndexFlatIP] = None
        self._metadatas: List[dict] = []

        if self.index_path.exists() and self.meta_path.exists():
            self._load_index()

    # ---------------------------
    # Helpers
    # ---------------------------
    def _hash(self, s: str) -> str:
        return hashlib.sha1(s.encode("utf-8")).hexdigest()

    def _save_index(self):
        if self._faiss_index is None:
            return
        faiss.write_index(self._faiss_index, str(self.index_path))
        with open(self.meta_path, "wb") as f:
            pickle.dump(self._metadatas, f)

    def _load_index(self):
        self._faiss_index = faiss.read_index(str(self.index_path))
        with open(self.meta_path, "rb") as f:
            self._metadatas = pickle.load(f)

    # ---------------------------
    # Embedding helper (batched)
    # ---------------------------
    def embed_texts(self, texts: List[str], batch_size: int = 64) -> np.ndarray:
        """
        Embeds list[str] into (n, d) float32 ndarray.
        Handles batching for large inputs.
        """
        if not texts:
            return np.zeros((0, 1), dtype="float32")

        all_embs = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self.embedding_client.embeddings.create(
                input=batch,
                model=self.embedding_model
            )
            embs = [r.embedding for r in response.data]
            all_embs.extend(embs)

        arr = np.array(all_embs, dtype="float32")
        faiss.normalize_L2(arr)
        return arr

    # ---------------------------
    # Index management
    # ---------------------------
    def add_files(self, file_paths: List[str], doc_id_prefix: Optional[str] = None, reindex: bool = False):
        """
        Adds local files to the FAISS index. If reindex=True, rebuilds index from scratch.
        """
        if reindex:
            self._faiss_index = None
            self._metadatas = []
            if self.index_path.exists():
                self.index_path.unlink()
            if self.meta_path.exists():
                self.meta_path.unlink()

        all_new_chunks, all_metadatas = [], []

        for path in file_paths:
            with open(path, "rb") as f:
                content_bytes = f.read()

            try:
                from ..rag.loaders import load_document
                text = load_document(content_bytes, os.path.splitext(path)[1].lower())
            except Exception:
                text = content_bytes.decode("utf-8", errors="ignore")

            if not text.strip():
                continue

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            chunks = splitter.split_text(text)

            for i, chunk in enumerate(chunks):
                doc_id = f"{doc_id_prefix or Path(path).stem}_{i}"
                all_new_chunks.append(chunk)
                all_metadatas.append({
                    "doc_id": doc_id,
                    "source": str(path),
                    "chunk_index": i,
                    "chunk_text": chunk,  # ✅ stored directly to avoid reloading later
                    "token_count": len(chunk.split())
                })

        if not all_new_chunks:
            print("⚠️ No new valid text found to index.")
            return

        vectors = self.embed_texts(all_new_chunks)

        d = vectors.shape[1]
        if self._faiss_index is None:
            self._faiss_index = faiss.IndexFlatIP(d)

        self._faiss_index.add(vectors)
        self._metadatas.extend(all_metadatas)
        self._save_index()
        print(f"✅ Added {len(all_new_chunks)} chunks to FAISS index")

    # ---------------------------
    # Retrieval with token limiter
    # ---------------------------
    def retrieve_context(self, query: str, k: int = 6) -> List[dict]:
        """
        Retrieve top-k chunks relevant to a query, token-limited.
        Returns: list[{"text": ..., "meta": ..., "score": ...}]
        """
        if self._faiss_index is None or len(self._metadatas) == 0:
            print("⚠️ No index loaded, returning empty context.")
            return []

        # Step 1: get top-k nearest chunks
        q_emb = self.embed_texts([query])
        D, I = self._faiss_index.search(q_emb, k)

        # Step 2: prepare encoder and join up to max token budget
        enc = tiktoken.encoding_for_model("gpt-4-turbo")
        total_tokens, results = 0, []

        for i, idx in enumerate(I[0]):
            if idx < 0 or idx >= len(self._metadatas):
                continue

            meta = self._metadatas[idx]
            text = meta.get("chunk_text", "")
            score = float(D[0][i])

            # token safety
            tokens = len(enc.encode(text))
            if total_tokens + tokens > self.max_tokens_per_query:
                break

            total_tokens += tokens
            results.append({"text": text, "meta": meta, "score": score})

        print(f"📚 Retrieved {len(results)} chunks ({total_tokens} tokens total)")
        return results

    def cleanup(self):
        """Optional cleanup hook."""
        pass
