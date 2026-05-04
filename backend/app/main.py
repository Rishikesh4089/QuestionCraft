# app/main.py
"""
FastAPI application factory.

The lifespan context manager handles startup and shutdown:
  Startup:  initialise logging, create shared OpenAI client and RAGPipeline singleton
  Shutdown: flush in-memory index cache

Import and run with:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI

from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.core.dependencies import set_pipeline
from app.core.logging import configure_logging
from app.core.middleware import RequestIDMiddleware, TimingMiddleware, register_exception_handlers
from app.rag.pipeline import RAGPipeline
from app.schemas.responses import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown logic."""
    settings = get_settings()

    # ── Startup ──────────────────────────────────────────────────────────
    configure_logging(level=settings.LOG_LEVEL, json_logs=settings.LOG_JSON)

    import logging
    logger = logging.getLogger(__name__)
    logger.info(
        f"Starting {settings.APP_NAME} v{settings.APP_VERSION} "
        f"[{settings.ENVIRONMENT}]"
    )

    # Create shared async OpenAI client (one per process)
    openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    # Create and register RAGPipeline singleton
    rag_pipeline = RAGPipeline(settings=settings, async_client=openai_client)
    set_pipeline(rag_pipeline)

    logger.info("RAGPipeline initialised and registered.")
    logger.info(f"Index directory: {settings.RAG_INDEX_DIR}")
    logger.info(f"Upload directory: {settings.UPLOAD_DIR}")

    yield  # ── Application running ─────────────────────────────────────

    # ── Shutdown ─────────────────────────────────────────────────────────
    rag_pipeline._store.clear_memory()
    logger.info("RAGPipeline memory cache cleared. Shutdown complete.")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Production-grade RAG-powered API for university question paper generation. "
            "Upload syllabus files, extract topic trees, and generate structured papers "
            "with Bloom's taxonomy alignment and hybrid retrieval."
        ),
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ── Middleware (order matters: outermost first) ────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TimingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # ── Exception handlers ────────────────────────────────────────────────
    register_exception_handlers(app)

    # ── Routes ────────────────────────────────────────────────────────────
    app.include_router(v1_router)

    # ── Health check ──────────────────────────────────────────────────────
    @app.get("/", response_model=HealthResponse, tags=["Health"])
    async def health():
        return HealthResponse(
            status="ok",
            service=settings.APP_NAME,
            version=settings.APP_VERSION,
            environment=settings.ENVIRONMENT,
        )

    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    async def health_check():
        return HealthResponse(
            status="ok",
            service=settings.APP_NAME,
            version=settings.APP_VERSION,
            environment=settings.ENVIRONMENT,
        )

    return app


app = create_app()