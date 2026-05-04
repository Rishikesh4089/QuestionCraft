# app/core/dependencies.py
"""
FastAPI dependency providers.

All shared resources (RAGPipeline, Settings) are injected via Depends().
This eliminates global state and makes testing straightforward —
override any dependency with app.dependency_overrides[dep] = mock.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from  app.core.config import Settings, get_settings
from  app.rag.pipeline import RAGPipeline

# ── Settings ─────────────────────────────────────────────────────────────────

SettingsDep = Annotated[Settings, Depends(get_settings)]


# ── RAG Pipeline ─────────────────────────────────────────────────────────────
# The pipeline is constructed once at startup (in main.py lifespan) and stored
# on app.state.  This dependency retrieves it from there.

def get_rag_pipeline(settings: SettingsDep) -> RAGPipeline:
    """
    Retrieve the application-scoped RAGPipeline singleton.

    The pipeline is initialised during the FastAPI lifespan (startup event)
    and attached to app.state.rag_pipeline.  Injecting it via Depends ensures
    it is never None at request time.
    """
    from fastapi import Request
    # We use a module-level singleton to avoid the circular import that would
    # arise from importing `app` here.  The pipeline is created in main.py and
    # stored in this module's _pipeline variable via set_pipeline().
    if _pipeline is None:
        raise RuntimeError(
            "RAGPipeline not initialised. "
            "Ensure main.py lifespan startup has completed before handling requests."
        )
    return _pipeline


_pipeline: RAGPipeline | None = None


def set_pipeline(pipeline: RAGPipeline) -> None:
    """Called once during app startup to register the pipeline singleton."""
    global _pipeline
    _pipeline = pipeline


RAGPipelineDep = Annotated[RAGPipeline, Depends(get_rag_pipeline)]