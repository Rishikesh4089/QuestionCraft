# app/rag/loaders/registry.py
"""
Loader registry.

Usage:
    from app.rag.loaders.registry import load_document
    text = load_document(Path("/path/to/file.pdf"))
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from  app.core.exceptions import UnsupportedFileTypeError, EmptyDocumentError
from  app.rag.loaders.base import BaseLoader
from  app.rag.loaders.pdf import PDFLoader
from  app.rag.loaders.extras import PowerPointLoader, CSVLoader, TextLoader

logger = logging.getLogger(__name__)


def _build_registry(enable_ocr: bool = True) -> dict[str, BaseLoader]:
    loaders: list[BaseLoader] = [
        PDFLoader(enable_ocr=enable_ocr),
        PowerPointLoader(),
        CSVLoader(),
        TextLoader(),
    ]
    registry: dict[str, BaseLoader] = {}
    for loader in loaders:
        for ext in loader.supported_extensions:
            registry[ext] = loader
    return registry


# Module-level registry (initialised lazily with default settings)
_REGISTRY: Optional[dict[str, BaseLoader]] = None


def get_registry(enable_ocr: bool = True) -> dict[str, BaseLoader]:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = _build_registry(enable_ocr=enable_ocr)
    return _REGISTRY


def load_document(path: Path, enable_ocr: bool = True) -> str:
    """
    Load and extract text from a document file.

    Raises:
        UnsupportedFileTypeError: If no loader handles this file extension.
        EmptyDocumentError: If the file produces no extractable text.
        FileReadError: If the loader fails to read the file.
    """
    ext = path.suffix.lower()
    registry = get_registry(enable_ocr=enable_ocr)
    loader = registry.get(ext)

    if loader is None:
        supported = sorted(registry.keys())
        raise UnsupportedFileTypeError(
            f"Unsupported file type: '{ext}'",
            detail=f"Supported types: {', '.join(supported)}",
            context={"extension": ext, "path": str(path)},
        )

    logger.debug(f"Loading {path.name} with {type(loader).__name__}")
    text = loader.load(path)

    if not text or not text.strip():
        raise EmptyDocumentError(
            f"No text extracted from {path.name}",
            detail="The file may be empty, password-protected, or contain only images.",
            context={"path": str(path)},
        )

    return text