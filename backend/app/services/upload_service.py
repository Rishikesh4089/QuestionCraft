# app/services/upload_service.py
"""
Upload service — manages the file lifecycle for API requests.

UploadService is used as an async context manager:

    async with UploadService(settings) as svc:
        paths = await svc.save(files)
        # use paths...
    # All saved files are deleted here, even on exception

This guarantees uploaded files are never leaked on error.
"""
from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import List

from fastapi import UploadFile

from  app.core.config import Settings

logger = logging.getLogger(__name__)


class UploadService:
    """
    Manages temporary file storage for API request uploads.

    Usage:
        async with UploadService(settings) as svc:
            paths = await svc.save(uploaded_files)
    """

    def __init__(self, settings: Settings) -> None:
        self._upload_dir = Path(settings.UPLOAD_DIR)
        self._saved: List[Path] = []

    async def __aenter__(self) -> "UploadService":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self.cleanup()

    async def save(self, files: List[UploadFile]) -> List[Path]:
        """
        Save a list of uploaded files to the upload directory.

        Returns:
            List of absolute Path objects for the saved files.
        """
        paths: List[Path] = []
        for upload in files:
            path = await self._save_one(upload)
            paths.append(path)
            self._saved.append(path)
        return paths

    async def save_one(self, upload: UploadFile) -> Path:
        """Save a single uploaded file. Returns its absolute Path."""
        path = await self._save_one(upload)
        self._saved.append(path)
        return path

    def cleanup(self) -> None:
        """Delete all files saved during this session."""
        for path in self._saved:
            try:
                if path.exists():
                    path.unlink()
                    logger.debug(f"Cleaned up: {path.name}")
            except Exception as exc:
                logger.warning(f"Failed to clean up {path}: {exc}")
        self._saved.clear()

    async def _save_one(self, upload: UploadFile) -> Path:
        self._upload_dir.mkdir(parents=True, exist_ok=True)
        # Sanitise filename: strip path traversal, collapse spaces
        safe_name = Path(upload.filename or "upload").name.replace(" ", "_")
        dest = self._upload_dir / safe_name

        # If a file with the same name exists from a prior request, make unique
        if dest.exists():
            import uuid
            stem = dest.stem
            dest = dest.with_name(f"{stem}_{uuid.uuid4().hex[:8]}{dest.suffix}")

        with open(dest, "wb") as f:
            shutil.copyfileobj(upload.file, f)

        logger.debug(f"Saved upload: {dest.name} ({dest.stat().st_size} bytes)")
        return dest