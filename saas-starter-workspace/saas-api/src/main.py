"""saas-api FastAPI application entrypoint (DDD)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.app.main import create_app

# <<<inject:imports>>>


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Coordinate startup/shutdown hooks contributed by RapidKit modules."""

    _ = app  # ensure the app reference stays available for injected hooks
    # <<<inject:startup>>>
    try:
        yield
    finally:
        # <<<inject:shutdown>>>
        pass


app: FastAPI = create_app(
    title="saas-api",
    description="Domain-driven FastAPI service generated with RapidKit",
    version="0.1.0",
    lifespan=lifespan,
)

# <<<inject:routes>>>