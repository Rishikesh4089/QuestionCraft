# app/rag/indexer/chunker.py
"""
Token-aware text chunker.

Uses LangChain's RecursiveCharacterTextSplitter with a tiktoken length
function so chunk sizes are measured in tokens, not characters.
"""
from __future__ import annotations

import logging
from typing import List

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

_ENCODING = tiktoken.get_encoding("cl100k_base")

_SEPARATORS = ["\n\n\n", "\n\n", "\n", ". ", " ", ""]


def count_tokens(text: str) -> int:
    """Count tiktoken tokens in a string."""
    return len(_ENCODING.encode(text))


def encode(text: str) -> list[int]:
    return _ENCODING.encode(text)


def decode(tokens: list[int]) -> str:
    return _ENCODING.decode(tokens)


def chunk_text(
    text: str,
    chunk_size: int = 400,
    chunk_overlap: int = 60,
) -> List[str]:
    """
    Split *text* into token-bounded chunks.

    Args:
        text: Raw extracted text from a document.
        chunk_size: Maximum tokens per chunk.
        chunk_overlap: Overlap in tokens between adjacent chunks.

    Returns:
        List of non-empty text chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=count_tokens,
        separators=_SEPARATORS,
        keep_separator=False,
    )
    chunks = splitter.split_text(text)
    non_empty = [c for c in chunks if c.strip()]
    logger.debug(f"Chunked text into {len(non_empty)} chunks ({chunk_size}t / {chunk_overlap}t overlap)")
    return non_empty