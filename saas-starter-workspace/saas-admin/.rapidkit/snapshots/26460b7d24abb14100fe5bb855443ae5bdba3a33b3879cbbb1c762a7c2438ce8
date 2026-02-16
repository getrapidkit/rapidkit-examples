"""FastAPI routes exposing Users Core metadata and features."""

from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, FastAPI, status

from src.modules.free.users.users_core.users_core import (
    MODULE_FEATURES,
    get_users_core_metadata as _get_users_core_metadata,
)
from src.health.users_core import (
    build_health_snapshot,
    render_health_snapshot,
)

router = APIRouter(prefix="/api/users-core", tags=["users-core"])


@router.get("/metadata", status_code=status.HTTP_200_OK)
async def get_users_core_metadata() -> Dict[str, object]:
    """Expose normalized metadata describing the Users Core configuration."""

    metadata = _get_users_core_metadata()
    return dict(metadata)


@router.get("/features", status_code=status.HTTP_200_OK)
async def list_users_core_features() -> Dict[str, object]:
    """Return the list of advertised capabilities for the Users Core module."""

    return {"features": list(MODULE_FEATURES)}


@router.get("/health", status_code=status.HTTP_200_OK)
async def get_users_core_health() -> Dict[str, object]:
    """Return health snapshot for the Users Core subsystem."""

    metadata = _get_users_core_metadata()
    snapshot = build_health_snapshot(metadata)
    return render_health_snapshot(snapshot)


def register_users_core_routes(app: FastAPI) -> None:
    """Attach the Users Core metadata routes to a FastAPI application."""

    app.include_router(router)


__all__ = [
    "get_users_core_health",
    "get_users_core_metadata",
    "list_users_core_features",
    "register_users_core_routes",
    "router",
]
