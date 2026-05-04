# app/api/v1/router.py
"""
Aggregates all v1 API routers into a single router mounted at /api/v1.
"""
from  app.api.v1 import paper, regenerate
from fastapi import APIRouter

from app.api.v1 import utilities

router = APIRouter(prefix="/api/v1")

router.include_router(paper.router)
router.include_router(regenerate.router)
router.include_router(utilities.router)