"""Shared registry for aggregating RapidKit module health routers."""

from __future__ import annotations

import logging
from typing import Any, Callable, Iterable, List

logger = logging.getLogger(__name__)

try:
    from fastapi import APIRouter
except ImportError:  # pragma: no cover - FastAPI not installed yet
    APIRouter = None  # type: ignore[assignment]

try:
    from fastapi import FastAPI
except ImportError:  # pragma: no cover - FastAPI not installed yet
    FastAPI = None  # type: ignore[assignment]

try:  # pragma: no cover - defensive import guarding
    from src.health import (
        iter_health_registrars as _core_iter_registrars,
        list_health_routes as _core_list_health_routes,
    )
except ImportError:  # pragma: no cover - registry not generated yet

    def _core_iter_registrars() -> Iterable[Callable[[Any], None]]:
        return ()

    def _core_list_health_routes(prefix: str = "/api/health") -> List[dict[str, Any]]:
        return []


def _collect_registrars() -> List[Callable[[Any], None]]:
    registrars: List[Callable[[Any], None]] = []
    for registrar in _core_iter_registrars():
        if callable(registrar):
            registrars.append(registrar)
    return registrars


def build_health_router(*, title: str = "RapidKit Module Health"):
    """Construct an APIRouter aggregating all registered module health routes."""

    if APIRouter is None or FastAPI is None:
        raise RuntimeError(
            "FastAPI must be installed to use the shared health registry"
        )

    staging_app = FastAPI(title=title)
    for registrar in _collect_registrars():
        try:
            registrar(staging_app)
        except Exception as exc:  # pragma: no cover - defensive guard  # noqa: BLE001
            logger.warning("Health registrar failed; skipping", exc_info=exc)
            continue

    router = APIRouter()
    router.include_router(staging_app.router)
    return router


def list_registered_health_routes(prefix: str = "/api/health") -> List[dict[str, Any]]:
    """Expose metadata for all registered module health endpoints."""

    try:
        return list(_core_list_health_routes(prefix=prefix))
    except Exception as exc:  # pragma: no cover - defensive guard  # noqa: BLE001
        logger.warning("Listing health routes failed", exc_info=exc)
        return []


__all__ = ["build_health_router", "list_registered_health_routes"]
