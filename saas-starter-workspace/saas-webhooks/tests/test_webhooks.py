"""Integration tests for webhook endpoints."""

from __future__ import annotations

import hashlib
import hmac
import json

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def _signature(secret: str, payload: dict, timestamp: str = "1700000000") -> str:
    body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    signed = f"{timestamp}.{body}".encode("utf-8")
    digest = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={digest}"


def test_webhook_rejects_invalid_signature(monkeypatch) -> None:
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test")
    payload = {"id": "evt_invalid_1", "type": "customer.subscription.created", "data": {"id": "sub_1"}}
    response = client.post(
        "/api/webhooks/stripe",
        json=payload,
        headers={"stripe-signature": "t=1,v1=bad"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid webhook signature"


def test_webhook_accepts_event_and_lists_logs(monkeypatch) -> None:
    secret = "whsec_test"
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", secret)
    payload = {
        "id": "evt_ok_1",
        "type": "customer.subscription.updated",
        "data": {"subscription_id": "sub_123", "status": "active"},
    }
    signature = _signature(secret, payload)

    intake_response = client.post(
        "/api/webhooks/stripe",
        json=payload,
        headers={"stripe-signature": signature},
    )
    assert intake_response.status_code == 202
    assert intake_response.json()["status"] == "accepted"

    logs_response = client.get("/api/webhooks/logs")
    assert logs_response.status_code == 200
    body = logs_response.json()
    assert body["total"] >= 1
    assert any(item["event_id"] == "evt_ok_1" for item in body["items"])


def test_webhook_replay_existing_event() -> None:
    replay_response = client.post("/api/webhooks/replay/evt_ok_1")
    assert replay_response.status_code == 200
    replay_payload = replay_response.json()
    assert replay_payload["status"] == "replay_accepted"
    assert replay_payload["event_id"] == "evt_ok_1"


def test_webhook_replay_missing_event_returns_404() -> None:
    replay_response = client.post("/api/webhooks/replay/evt_missing")
    assert replay_response.status_code == 404
    assert replay_response.json()["detail"] == "Webhook event not found"
