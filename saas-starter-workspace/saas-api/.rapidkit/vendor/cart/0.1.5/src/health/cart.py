"""Health helpers for Cart."""

from __future__ import annotations

from datetime import datetime, timezone
import time
from typing import Any, Dict, Mapping, Optional

from src.modules.free.billing.cart.cart import CartService, CartValidationError


DEFAULT_HEALTH_PREFIX = "/api/health/module/cart"
_START_TS = time.monotonic()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_health_payload(status: str = "ok", **extra: Any) -> Dict[str, Any]:
    payload = {
        "module": "cart",
        "status": status,
        "checked_at": _now_iso(),
        "version": "0.1.5",
        "uptime": max(0.0, time.monotonic() - _START_TS),
    }
    if extra:
        payload.update(extra)
    return payload


def run_cart_health_check(service: CartService | None = None) -> Dict[str, Any]:
    """Return health diagnostics for the cart module."""

    service = service or CartService()
    try:
        diagnostics = service.inspect()
    except CartValidationError as exc:
        return build_health_payload(status="error", detail=str(exc))
    except Exception as exc:  # pragma: no cover - defensive hardening
        return build_health_payload(status="error", detail=str(exc))

    metrics = diagnostics.get("metrics", {})
    configuration = diagnostics.get("configuration", {})

    return build_health_payload(
        status="ok",
        metrics=metrics,
        configuration=configuration,
    )


def ensure_health_state(
    *,
    service: CartService | None = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Return the health payload enriched with optional metadata."""

    payload = run_cart_health_check(service)
    if metadata:
        payload.setdefault("metadata", {}).update(dict(metadata))
    return payload


def build_health_router(prefix: str = DEFAULT_HEALTH_PREFIX) -> Any:
    """Build a FastAPI router exposing the module health payload."""

    try:
        from fastapi import APIRouter  # type: ignore
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("fastapi is required to build the health router") from exc

    router = APIRouter(prefix=prefix, tags=["health", "Cart"])

    @router.get("", summary="Cart health")
    async def read_health() -> Dict[str, Any]:
        return ensure_health_state()

    return router


def create_health_router(prefix: str = DEFAULT_HEALTH_PREFIX) -> Any:
    return build_health_router(prefix=prefix)


def register_cart_health(app: Any, prefix: str = DEFAULT_HEALTH_PREFIX) -> None:
    """Attach module health routes to a FastAPI app."""

    router = build_health_router(prefix=prefix)
    app.include_router(router)


try:
    router = build_health_router()
except Exception:  # pragma: no cover - optional FastAPI or runtime failures
    router = None


__all__ = [
    "build_health_payload",
    "build_health_router",
    "create_health_router",
    "register_cart_health",
    "router",
    "run_cart_health_check",
    "ensure_health_state",
    "DEFAULT_HEALTH_PREFIX",
]
