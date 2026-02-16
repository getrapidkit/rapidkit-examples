"""Shared health helpers for the Users Core module."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Mapping, MutableMapping, Sequence

try:
    from fastapi import APIRouter, status

    _FASTAPI_AVAILABLE = True
except ImportError:  # pragma: no cover - FastAPI optional for vendor runtime
    APIRouter = None  # type: ignore[assignment]
    status = None  # type: ignore[assignment]
    _FASTAPI_AVAILABLE = False

from src.modules.free.users.users_core.users_core import (
    MODULE_FEATURES,
    describe_users_core,
    get_users_core_metadata,
)
from src.modules.free.users.users_core.users_core_types import UsersCoreHealthSnapshot, as_dict


_START_MONOTONIC = time.monotonic()

DEFAULT_FEATURES: tuple[str, ...] = MODULE_FEATURES


def build_health_snapshot(
    metadata: Mapping[str, Any] | None = None,
    *,
    module_name: str = "users_core",
    status: str | None = None,
    detail: str | None = None,
    features: Sequence[str] | None = None,
) -> UsersCoreHealthSnapshot:
    """Construct a Users Core health snapshot from raw metadata."""

    base_metadata: MutableMapping[str, Any]
    if metadata is None:
        base_metadata = dict(get_users_core_metadata())
    else:
        base_metadata = dict(metadata)

    feature_set = tuple(features) if features is not None else DEFAULT_FEATURES
    base_metadata.setdefault("module", module_name)
    base_metadata.setdefault("checked_at", datetime.now(timezone.utc).isoformat())
    if status is not None:
        base_metadata["status"] = status
    if feature_set:
        base_metadata["features"] = list(feature_set)
    return UsersCoreHealthSnapshot.from_mapping(
        base_metadata,
        module_name=module_name,
        features=feature_set,
        detail=detail,
    )


def render_health_snapshot(snapshot: UsersCoreHealthSnapshot) -> MutableMapping[str, Any]:
    """Serialize a Users Core health snapshot into JSON-compatible payload."""

    return as_dict(snapshot)


def build_metadata(metadata: Mapping[str, Any] | None = None) -> MutableMapping[str, Any]:
    """Return serialized metadata for the Users Core module."""

    snapshot = build_health_snapshot(metadata)
    return as_dict(snapshot)


DEFAULT_HEALTH_PREFIX = "/api/health/module/users-core"


def _normalise_prefix(prefix: str) -> str:
    if not prefix:
        return ""
    if not prefix.startswith("/"):
        prefix = "/" + prefix
    return prefix.rstrip("/")


def build_health_router(prefix: str = DEFAULT_HEALTH_PREFIX) -> Any:
    """Create a FastAPI router that exposes the Users Core health endpoint."""

    if not _FASTAPI_AVAILABLE:
        raise RuntimeError("FastAPI must be installed to build Users Core health routers")

    router = APIRouter(prefix=_normalise_prefix(prefix), tags=["health", "users-core"])

    @router.get("", status_code=status.HTTP_200_OK)
    async def users_core_health_check() -> Any:  # pragma: no cover - exercised in integration tests
        snapshot = build_health_snapshot(get_users_core_metadata(), features=MODULE_FEATURES)
        payload = render_health_snapshot(snapshot)
        payload.setdefault("version", "0.1.7")
        payload.setdefault("uptime", max(0.0, time.monotonic() - _START_MONOTONIC))
        return payload

    return router


def register_users_core_health(app: Any, prefix: str = DEFAULT_HEALTH_PREFIX) -> None:
    """Attach the Users Core health router to the given FastAPI application."""

    if not _FASTAPI_AVAILABLE:
        raise RuntimeError("FastAPI must be installed to register Users Core health routes")

    app.include_router(build_health_router(prefix=prefix))


if _FASTAPI_AVAILABLE:
    router = build_health_router()
else:  # pragma: no cover
    router = None


__all__ = [
    "DEFAULT_FEATURES",
    "DEFAULT_HEALTH_PREFIX",
    "build_health_snapshot",
    "build_health_router",
    "build_metadata",
    "register_users_core_health",
    "render_health_snapshot",
    "router",
]
