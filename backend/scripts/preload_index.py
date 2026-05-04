#!/usr/bin/env python
# scripts/preload_index.py
"""
CLI script to pre-build indexes for a set of syllabus files.

Use this to warm up the index cache before deployment or after
adding new syllabus documents, so the first /generate-paper/ request
doesn't bear the indexing cost.

Usage:
    python scripts/preload_index.py path/to/syllabus1.pdf path/to/syllabus2.pptx
    python scripts/preload_index.py --dir ./syllabuses/
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Ensure project root is on sys.path when running as a script
sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import AsyncOpenAI

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.rag.pipeline import RAGPipeline


async def main(file_paths: list[Path], force: bool) -> None:
    settings = get_settings()
    configure_logging(level=settings.LOG_LEVEL)
    logger = logging.getLogger("preload")

    if not file_paths:
        logger.error("No files provided.")
        sys.exit(1)

    logger.info(f"Pre-loading index for {len(file_paths)} file(s)…")
    for p in file_paths:
        logger.info(f"  {p}")

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    pipeline = RAGPipeline(settings=settings, async_client=client)

    key = await pipeline.ensure_indexed(file_paths, force_rebuild=force)
    logger.info(f"✅ Index ready: key={key}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pre-build RAG index for syllabus files.")
    parser.add_argument("files", nargs="*", type=Path, help="Syllabus file paths")
    parser.add_argument(
        "--dir", type=Path, default=None,
        help="Directory of syllabus files (all supported types)"
    )
    parser.add_argument(
        "--force", action="store_true", default=False,
        help="Force rebuild even if index already exists"
    )
    args = parser.parse_args()

    paths: list[Path] = list(args.files)
    if args.dir:
        supported = {".pdf", ".pptx", ".ppt", ".csv", ".tsv", ".txt", ".md"}
        paths += [p for p in args.dir.iterdir() if p.suffix.lower() in supported]

    asyncio.run(main(paths, force=args.force))