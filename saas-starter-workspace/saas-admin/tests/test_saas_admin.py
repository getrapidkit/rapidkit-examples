"""Integration tests for SaaS admin endpoints."""

from __future__ import annotations

import asyncio
import os

from fastapi.testclient import TestClient

os.environ.setdefault("RAPIDKIT_AUTH_CORE_PEPPER", "rapidkit-dev-auth-pepper")
os.environ.setdefault("SAAS_ADMIN_EMAIL", "admin@example.com")
os.environ.setdefault("SAAS_ADMIN_PASSWORD", "AdminPass123!")

from src.main import app
from src.modules.free.users.users_core.core.users.dependencies import get_users_repository
from src.modules.free.users.users_core.core.users.dto import UserCreateDTO
from src.modules.free.users.users_core.core.users.in_memory_repository import InMemoryUserRepository
from src.modules.free.users.users_core.core.users.service import UsersService

client = TestClient(app)


def _admin_headers() -> dict[str, str]:
    response = client.post(
        "/api/admin/auth/login",
        json={"email": "admin@example.com", "password": "AdminPass123!"},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _seed_user() -> str:
    repo = get_users_repository()
    assert isinstance(repo, InMemoryUserRepository)
    repo._users.clear()

    service = UsersService(repo)
    created = asyncio.run(
        service.create_user(
            UserCreateDTO(
                email="seeded-user@example.com",
                full_name="Seeded User",
                metadata={"source": "test"},
            )
        )
    )
    return created.id


def test_saas_admin_endpoints_flow() -> None:
    user_id = _seed_user()
    headers = _admin_headers()

    users = client.get("/api/admin/users", headers=headers)
    assert users.status_code == 200, users.text
    assert users.json()["count"] >= 1

    ban = client.put(f"/api/admin/users/{user_id}/ban", headers=headers)
    assert ban.status_code == 200, ban.text
    assert ban.json()["status"] == "banned"
    assert ban.json()["user"]["status"] == "disabled"

    subscriptions = client.get("/api/admin/subscriptions", headers=headers)
    assert subscriptions.status_code == 200, subscriptions.text
    assert "subscriptions" in subscriptions.json()

    users_metrics = client.get("/api/admin/metrics/users", headers=headers)
    assert users_metrics.status_code == 200, users_metrics.text
    assert users_metrics.json()["disabled_users"] >= 1

    revenue_metrics = client.get("/api/admin/metrics/revenue", headers=headers)
    assert revenue_metrics.status_code == 200, revenue_metrics.text
    assert revenue_metrics.json()["monthly_recurring_revenue"] >= 0

    health = client.get("/api/admin/health", headers=headers)
    assert health.status_code == 200, health.text
    assert health.json()["status"] == "ok"


def test_admin_auth_rejects_invalid_credentials() -> None:
    login = client.post(
        "/api/admin/auth/login",
        json={"email": "admin@example.com", "password": "wrong-password"},
    )
    assert login.status_code == 401
