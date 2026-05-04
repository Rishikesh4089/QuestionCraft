# app/core/middleware.py
"""
Production middleware stack:
  1. RequestIDMiddleware  — Assigns X-Request-ID to every request
  2. TimingMiddleware     — Adds X-Process-Time header to responses
  3. register_exception_handlers — Maps domain exceptions → HTTP responses
"""
from __future__ import annotations

import logging
import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from  app.core.exceptions import QuestionCraftError

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Injects a unique X-Request-ID into every request/response.
    Uses client-supplied header if present, otherwise generates a UUID4.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        # Store on request state so handlers can access it
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class TimingMiddleware(BaseHTTPMiddleware):
    """Adds X-Process-Time (milliseconds) to every response."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Process-Time"] = f"{elapsed_ms:.1f}ms"
        logger.debug(
            "Request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(elapsed_ms, 1),
            },
        )
        return response


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception → HTTP response mappings on the FastAPI app."""

    @app.exception_handler(QuestionCraftError)
    async def handle_domain_error(request: Request, exc: QuestionCraftError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.warning(
            f"Domain error [{exc.error_code}]: {exc.message}",
            extra={"request_id": request_id, "context": exc.context},
        )
        body = exc.to_dict()
        if request_id:
            body["request_id"] = request_id
        return JSONResponse(status_code=exc.status_code, content=body)

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.exception(
            f"Unhandled exception on {request.method} {request.url.path}",
            extra={"request_id": request_id},
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
                "request_id": request_id,
            },
        )