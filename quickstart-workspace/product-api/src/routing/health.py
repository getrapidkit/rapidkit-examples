"""Health endpoints."""

from __future__ import annotations

from time import monotonic

from fastapi import APIRouter

router = APIRouter(tags=["health"])

_START_TIME = monotonic()


@router.get("/", summary="Health check")
async def heartbeat() -> dict[str, object]:
    """Return basic service heartbeat."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "uptime": monotonic() - _START_TIME,
        "module": "app",
    }