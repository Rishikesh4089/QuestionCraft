# app/rag/loaders/pdf.py
"""
PDF loader with OCR fallback for scanned documents.

Primary extraction: pypdf (text-based PDFs)
Fallback: pdf2image + pytesseract (scanned/image PDFs)
"""
from __future__ import annotations

import logging
from pathlib import Path

from  app.core.exceptions import FileReadError
from  app.rag.loaders.base import BaseLoader

logger = logging.getLogger(__name__)

# Optional OCR dependencies
try:
    from pdf2image import convert_from_path as _pdf_to_images  # type: ignore
    import pytesseract  # type: ignore
    _HAS_OCR = True
except ImportError:
    _HAS_OCR = False
    logger.info("OCR unavailable: install pdf2image and pytesseract for scanned PDF support.")


class PDFLoader(BaseLoader):
    """Load text from PDF files, with optional OCR fallback."""

    def __init__(self, enable_ocr: bool = True, min_text_chars: int = 50) -> None:
        self._ocr_enabled = enable_ocr and _HAS_OCR
        self._min_text_chars = min_text_chars

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        return (".pdf",)

    def load(self, path: Path) -> str:
        text = self._pypdf_extract(path)

        if len(text.strip()) < self._min_text_chars:
            if self._ocr_enabled:
                logger.info(f"Sparse text from pypdf ({len(text)} chars) — running OCR: {path.name}")
                text = self._ocr_extract(path)
            else:
                logger.warning(
                    f"Sparse text from {path.name} ({len(text)} chars) and OCR is disabled."
                )

        return text

    def _pypdf_extract(self, path: Path) -> str:
        try:
            import pypdf  # type: ignore
            reader = pypdf.PdfReader(str(path))
            pages = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    pages.append(page_text)
            return "\n".join(pages)
        except Exception as exc:
            logger.warning(f"pypdf extraction failed for {path.name}: {exc}")
            return ""

    def _ocr_extract(self, path: Path) -> str:
        try:
            images = _pdf_to_images(str(path))  # type: ignore[arg-type]
            return "\n".join(pytesseract.image_to_string(img) for img in images)  # type: ignore[misc]
        except Exception as exc:
            logger.error(f"OCR extraction failed for {path.name}: {exc}")
            raise FileReadError(
                f"Could not extract text from {path.name}",
                detail=f"Both pypdf and OCR extraction failed. OCR error: {exc}",
                context={"path": str(path)},
            ) from exc