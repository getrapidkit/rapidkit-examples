"""API router assembly."""

from __future__ import annotations

from fastapi import APIRouter

from .health import router as health_router
from .examples import router as examples_router
from .webhooks import router as webhooks_router

# <<<inject:router-imports>>>

api_router = APIRouter()

api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(examples_router, prefix="/examples", tags=["examples"])
api_router.include_router(webhooks_router, prefix="/webhooks", tags=["webhooks"])
# <<<inject:router-mount>>>