# app/rag/loaders/base.py
"""Abstract document loader interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class BaseLoader(ABC):
    """
    All loaders implement this interface.
    A loader receives a file path and returns extracted plain text.
    """

    @abstractmethod
    def load(self, path: Path) -> str:
        """
        Extract text from the file at *path*.

        Returns:
            Extracted text (may be empty string if the file has no readable content).

        Raises:
            FileReadError: If extraction fails unrecoverably.
        """
        ...

    def can_load(self, path: Path) -> bool:
        """Return True if this loader handles the given file extension."""
        return path.suffix.lower() in self.supported_extensions

    @property
    @abstractmethod
    def supported_extensions(self) -> tuple[str, ...]:
        """Tuple of lowercase extensions this loader handles, e.g. ('.pdf',)."""
        ...