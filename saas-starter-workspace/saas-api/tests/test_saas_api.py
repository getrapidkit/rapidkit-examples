"""Integration tests for SaaS starter API endpoints."""

from __future__ import annotations

import os
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient

os.environ.setdefault("RAPIDKIT_SESSION_SECRET", "rapidkit-dev-session-secret")
os.environ.setdefault("RAPIDKIT_AUTH_CORE_PEPPER", "rapidkit-dev-auth-pepper")
os.environ.setdefault("GOOGLE_OAUTH_CLIENT_ID", "dev-google-client-id")
os.environ.setdefault("GOOGLE_OAUTH_CLIENT_SECRET", "dev-google-client-secret")
os.environ.setdefault("GITHUB_OAUTH_CLIENT_ID", "dev-github-client-id")
os.environ.setdefault("GITHUB_OAUTH_CLIENT_SECRET", "dev-github-client-secret")

from src.main import app

client = TestClient(app)


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_saas_primary_endpoints_flow() -> None:
    register_payload = {
        "email": "founder@example.com",
        "password": "StrongPass1234",
        "full_name": "SaaS Founder",
    }
    register = client.post("/api/auth/register", json=register_payload)
    assert register.status_code == 201, register.text
    auth_bundle = register.json()
    token = auth_bundle["access_token"]

    me = client.get("/api/auth/me", headers=_auth_headers(token))
    assert me.status_code == 200, me.text
    assert me.json()["user"]["email"] == register_payload["email"]

    profile_update = client.put(
        "/api/users/profile",
        json={"display_name": "Founder", "timezone": "UTC", "biography": "Building SaaS"},
        headers=_auth_headers(token),
    )
    assert profile_update.status_code == 200, profile_update.text

    profile_get = client.get("/api/users/profile", headers=_auth_headers(token))
    assert profile_get.status_code == 200, profile_get.text
    assert profile_get.json()["display_name"] == "Founder"

    plans = client.get("/api/subscriptions/plans", headers=_auth_headers(token))
    assert plans.status_code == 200, plans.text
    assert len(plans.json()["plans"]) >= 1

    checkout = client.post(
        "/api/subscriptions/checkout",
        json={"plan_id": "growth"},
        headers=_auth_headers(token),
    )
    assert checkout.status_code == 201, checkout.text
    assert checkout.json()["checkout"]["status"] == "active"

    current_subscription = client.get("/api/subscriptions/current", headers=_auth_headers(token))
    assert current_subscription.status_code == 200, current_subscription.text
    assert current_subscription.json()["subscription"]["plan"]["id"] == "growth"

    payment_method = client.post(
        "/api/billing/payment-method",
        json={
            "type": "card",
            "provider": "stripe",
            "last4": "4242",
            "exp_month": 12,
            "exp_year": 2030,
        },
        headers=_auth_headers(token),
    )
    assert payment_method.status_code == 201, payment_method.text
    assert payment_method.json()["payment_method"]["last4"] == "4242"

    create_team = client.post("/api/teams", json={"name": "Core Team"}, headers=_auth_headers(token))
    assert create_team.status_code == 201, create_team.text

    teams = client.get("/api/teams", headers=_auth_headers(token))
    assert teams.status_code == 200, teams.text
    assert teams.json()["teams"][0]["name"] == "Core Team"


def test_oauth_authorize_and_callback_flow() -> None:
    authorize = client.get("/api/auth/oauth/google", follow_redirects=False)
    assert authorize.status_code == 307, authorize.text

    redirect_location = authorize.headers["location"]
    state = parse_qs(urlparse(redirect_location).query)["state"][0]

    callback = client.post(
        "/api/auth/oauth/google/callback",
        json={
            "state": state,
            "email": "oauth-user@example.com",
            "full_name": "OAuth User",
        },
    )
    assert callback.status_code == 200, callback.text
    payload = callback.json()
    assert payload["provider"] == "google"
    assert payload["user"]["email"] == "oauth-user@example.com"
