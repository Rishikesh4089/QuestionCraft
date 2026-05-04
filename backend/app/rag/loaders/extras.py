# app/rag/loaders/extras.py
"""
Additional document loaders:
  - PowerPointLoader  (.pptx)
  - CSVLoader         (.csv, .tsv)
  - TextLoader        (.txt, .md)
"""
from __future__ import annotations

import csv
import logging
from pathlib import Path

from  app.core.exceptions import FileReadError
from  app.rag.loaders.base import BaseLoader

logger = logging.getLogger(__name__)


class PowerPointLoader(BaseLoader):
    """Extract text from PowerPoint slides (.pptx)."""

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        return (".pptx", ".ppt")

    def load(self, path: Path) -> str:
        try:
            from  app.rag.loaders.pptx import Presentation  # type: ignore
        except ImportError as exc:
            raise FileReadError(
                "python-pptx is not installed. Run: pip install python-pptx",
                context={"path": str(path)},
            ) from exc

        try:
            prs = Presentation(str(path))
            parts: list[str] = []
            for slide_num, slide in enumerate(prs.slides, start=1):
                slide_texts: list[str] = []
                for shape in slide.shapes:
                    if shape.has_text_frame:
                        for para in shape.text_frame.paragraphs:
                            text = " ".join(run.text for run in para.runs if run.text.strip())
                            if text:
                                slide_texts.append(text)
                if slide_texts:
                    parts.append(f"[Slide {slide_num}]\n" + "\n".join(slide_texts))
            return "\n\n".join(parts)
        except Exception as exc:
            logger.error(f"PowerPoint extraction failed for {path.name}: {exc}")
            raise FileReadError(
                f"Could not read PowerPoint file: {path.name}",
                context={"path": str(path)},
            ) from exc


class CSVLoader(BaseLoader):
    """Extract text from CSV / TSV files."""

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        return (".csv", ".tsv")

    def load(self, path: Path) -> str:
        delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
        try:
            rows: list[str] = []
            with open(path, newline="", encoding="utf-8", errors="replace") as f:
                reader = csv.reader(f, delimiter=delimiter)
                for row in reader:
                    rows.append(" | ".join(cell.strip() for cell in row if cell.strip()))
            return "\n".join(rows)
        except Exception as exc:
            raise FileReadError(
                f"Could not read CSV file: {path.name}",
                context={"path": str(path)},
            ) from exc


class TextLoader(BaseLoader):
    """Load plain text files (.txt, .md)."""

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        return (".txt", ".md", ".rst")

    def load(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            raise FileReadError(
                f"Could not read text file: {path.name}",
                context={"path": str(path)},
            ) from exc