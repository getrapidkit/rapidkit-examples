"""Integration coverage for the Stripe Payment FastAPI bindings."""

from __future__ import annotations

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.template_integration]


def test_stripe_payment_metadata_snapshot() -> None:
    from src.modules.free.billing.stripe_payment.stripe_payment import StripePayment

    runtime = StripePayment()
    metadata = runtime.metadata()

    assert metadata["module"] == "stripe_payment"
    assert metadata["defaults"]["default_currency"].lower() == "usd"
    assert metadata["retry_policy"]["max_attempts"] == 3
    assert metadata["webhook"]["events"]
    assert metadata["environment"]["has_api_key"] is False


def test_fastapi_routes_expose_health_and_metadata() -> None:
    from fastapi import FastAPI, status
    from fastapi.testclient import TestClient

    from src.health.stripe_payment import register_stripe_payment_health
    from src.modules.free.billing.stripe_payment.routers.stripe_payment import build_router

    app = FastAPI()
    app.include_router(build_router())
    register_stripe_payment_health(app)

    client = TestClient(app)

    metadata_response = client.get("/stripe-payment/metadata")
    assert metadata_response.status_code == status.HTTP_200_OK
    payload = metadata_response.json()
    assert payload["module"] == "stripe_payment"
    assert payload["billing"]["allowed_currencies"]

    health_response = client.get("/stripe-payment/health")
    assert health_response.status_code == status.HTTP_200_OK
    health = health_response.json()
    assert health["status"] in {"ok", "degraded"}
    assert health["default_currency"]

    module_health = client.get("/api/health/module/stripe-payment")
    assert module_health.status_code == status.HTTP_200_OK
    assert module_health.json()["module"] == "stripe_payment"


def test_stripe_payment_config_defaults() -> None:
    from pathlib import Path

    config_path = Path("config/stripe_payment.yaml")
    assert config_path.exists(), "Expected generated config file to exist"

    raw = config_path.read_text(encoding="utf-8")
    assert "stripe_payment:" in raw
    assert "mode:" in raw
