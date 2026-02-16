"""Webhook endpoints for Stripe-style event intake and replay."""

from __future__ import annotations

import hashlib
import hmac
import os
import time
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from pydantic import BaseModel, Field

try:
    from src.modules.free.communication.notifications.core.notifications import (
        Notification,
        NotificationManager,
    )
except Exception:  # pragma: no cover - optional dependency fallback
    Notification = None  # type: ignore[assignment]
    NotificationManager = None  # type: ignore[assignment]


router = APIRouter(tags=["webhooks"])


class StripeWebhookRequest(BaseModel):
    """Incoming Stripe-style webhook payload."""

    id: str = Field(..., min_length=3)
    type: str = Field(..., min_length=3)
    data: dict[str, Any] = Field(default_factory=dict)
    created: int | None = None


class WebhookLogEntry(BaseModel):
    """Tracked lifecycle for webhook events."""

    event_id: str
    event_type: str
    status: str
    received_at: str
    processed_at: str | None = None
    replay_count: int = 0
    attempts: int = 0
    last_error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


_EVENTS: dict[str, WebhookLogEntry] = {}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_signature_header(header_value: str) -> tuple[str | None, str | None]:
    timestamp: str | None = None
    signature: str | None = None
    for part in header_value.split(","):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        if key == "t":
            timestamp = value
        if key == "v1":
            signature = value
    return timestamp, signature


def _verify_signature(body: bytes, header_value: str, secret: str) -> bool:
    timestamp, signature = _parse_signature_header(header_value)
    if not timestamp or not signature:
        return False

    signed_payload = f"{timestamp}.{body.decode('utf-8')}".encode("utf-8")
    expected = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


async def _dispatch_subscription_notifications(request: Request, event: StripeWebhookRequest) -> None:
    if Notification is None or NotificationManager is None:
        return

    manager = getattr(request.app.state, "notification_manager", None)
    if manager is None or not isinstance(manager, NotificationManager):
        return

    if not event.type.startswith("customer.subscription"):
        return

    recipient = os.getenv("WEBHOOKS_NOTIFY_EMAIL", "billing@example.com")
    title = f"Subscription Event: {event.type}"
    body = f"Processed event {event.id} with payload keys: {sorted(event.data.keys())}"
    await manager.send_notification(
        Notification(
            channel="email",
            recipient=recipient,
            title=title,
            body=body,
            metadata={"provider": "stripe", "event_id": event.id},
        )
    )


async def _process_event(request: Request, event: StripeWebhookRequest) -> None:
    record = _EVENTS[event.id]
    max_attempts = int(os.getenv("WEBHOOKS_MAX_RETRIES", "3"))
    record.attempts += 1

    try:
        await _dispatch_subscription_notifications(request, event)
        record.status = "processed"
        record.last_error = None
        record.processed_at = _utc_now()
    except Exception as exc:  # pragma: no cover - defensive runtime guard
        record.last_error = str(exc)
        record.status = "failed"
        if record.attempts < max_attempts:
            record.status = "retry_scheduled"


@router.post(
    "/stripe",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Receive Stripe webhook events",
)
async def receive_stripe_webhook(
    payload: StripeWebhookRequest,
    request: Request,
    background_tasks: BackgroundTasks,
) -> dict[str, Any]:
    """Validate signature, persist webhook log, and queue background processing."""

    raw_body = await request.body()
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_test")
    signature_header = request.headers.get("stripe-signature")

    if signature_header:
        if not _verify_signature(raw_body, signature_header, webhook_secret):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook signature")

    existing = _EVENTS.get(payload.id)
    if existing:
        return {
            "status": "duplicate",
            "event_id": payload.id,
            "attempts": existing.attempts,
            "replay_count": existing.replay_count,
        }

    _EVENTS[payload.id] = WebhookLogEntry(
        event_id=payload.id,
        event_type=payload.type,
        status="queued",
        received_at=_utc_now(),
        metadata={
            "provider": "stripe",
            "created": payload.created,
            "ingested_epoch": int(time.time()),
        },
    )

    background_tasks.add_task(_process_event, request, payload)
    return {"status": "accepted", "event_id": payload.id}


@router.get("/logs", summary="List webhook event logs")
def list_webhook_logs(limit: int = 100) -> dict[str, Any]:
    """Return recent webhook processing logs."""

    if limit < 1:
        limit = 1
    logs = list(_EVENTS.values())
    logs.sort(key=lambda entry: entry.received_at, reverse=True)
    return {
        "items": [entry.model_dump() for entry in logs[:limit]],
        "total": len(logs),
    }


@router.post("/replay/{event_id}", summary="Replay a previously ingested event")
async def replay_webhook_event(
    event_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
) -> dict[str, Any]:
    """Queue replay for an existing event, applying retry bookkeeping."""

    event = _EVENTS.get(event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook event not found")

    event.replay_count += 1
    event.status = "replay_queued"

    replay_payload = StripeWebhookRequest(
        id=event.event_id,
        type=event.event_type,
        data=event.metadata,
    )
    background_tasks.add_task(_process_event, request, replay_payload)

    return {
        "status": "replay_accepted",
        "event_id": event_id,
        "replay_count": event.replay_count,
    }
