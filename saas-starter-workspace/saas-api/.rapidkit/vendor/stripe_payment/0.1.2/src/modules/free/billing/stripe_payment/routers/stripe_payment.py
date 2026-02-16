"""FastAPI route definitions for Stripe Payment."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from ..stripe_payment import StripePayment


def build_router() -> APIRouter:
    router = APIRouter(prefix="/stripe-payment", tags=["Stripe Payment"])
    facade = StripePayment()

    @router.get("/health", summary="Stripe Payment health check")
    async def read_health() -> dict[str, Any]:
        return facade.health_check()

    @router.get("/metadata", summary="Stripe Payment metadata snapshot")
    async def read_metadata() -> dict[str, Any]:
        return facade.metadata()

    return router
