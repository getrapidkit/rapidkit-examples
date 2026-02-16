"""FastAPI router exposing Celery metadata and features."""

from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, FastAPI

from src.health.celery import build_health_snapshot, render_health_snapshot
from src.modules.free.tasks.celery.celery import MODULE_FEATURES, get_celery_metadata

router = APIRouter(prefix="/tasks/celery", tags=["tasks", "celery"])


@router.get("/metadata", response_model=Dict[str, object])
async def get_celery_metadata() -> Dict[str, object]:
    """Expose the configured Celery metadata."""

    metadata = get_celery_metadata(include_tasks=True)
    snapshot = build_health_snapshot(metadata)
    return render_health_snapshot(snapshot)


@router.get("/features", response_model=Dict[str, object])
async def list_celery_features() -> Dict[str, object]:
    """List capabilities advertised by the Celery module."""

    return {"features": list(MODULE_FEATURES)}


def register_celery_routes(app: FastAPI) -> None:
    """Attach the Celery metadata routes to a FastAPI application."""

    app.include_router(router)


__all__ = [
    "get_celery_metadata",
    "list_celery_features",
    "register_celery_routes",
    "router",
]
