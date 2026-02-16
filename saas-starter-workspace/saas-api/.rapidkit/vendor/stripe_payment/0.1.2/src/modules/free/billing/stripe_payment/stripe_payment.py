"""Runtime facade for the Stripe Payment module."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict

MODULE_NAME = "stripe_payment"
MODULE_TITLE = "Stripe Payment"

DEFAULTS: Dict[str, Any] = json.loads(
    """{
  "automatic_payment_methods": true,
  "capture_method": "automatic",
  "default_currency": "usd",
  "description_prefix": "RapidKit Checkout",
  "enabled": true,
  "metadata": {
    "product": "rapidkit",
    "source": "stripe-payment-module"
  },
  "mode": "test",
  "retry_attempts": 3,
  "statement_descriptor": "RapidKit Order"
}"""
) or {}

RETRY_POLICY: Dict[str, Any] = json.loads(
    """{
  "base_delay_seconds": 2.0,
  "max_attempts": 3,
  "max_delay_seconds": 30.0
}"""
) or {}

WEBHOOK: Dict[str, Any] = json.loads(
    """{
  "enabled": true,
  "endpoint_secret_env": "RAPIDKIT_STRIPE_WEBHOOK_SECRET",
  "events": [
    "payment_intent.succeeded",
    "payment_intent.payment_failed",
    "charge.refunded",
    "charge.dispute.created"
  ],
  "tolerance_seconds": 300
}"""
) or {}

FEATURE_FLAGS: Dict[str, Any] = json.loads(
    """{
  "allow_manual_capture": true,
  "emit_metrics": true,
  "enable_idempotency_keys": true,
  "verify_webhooks": true
}"""
) or {}

BILLING: Dict[str, Any] = json.loads(
    """{
  "allowed_currencies": [
    "usd",
    "eur",
    "gbp"
  ],
  "default_payment_method_types": [
    "card",
    "us_bank_account"
  ],
  "maximum_amount": 5000000,
  "minimum_amount": 50
}"""
) or {}

NETWORK: Dict[str, Any] = json.loads(
    """{
  "max_connections": 4,
  "timeout_seconds": 10.0
}"""
) or {}

METADATA_KEYS: Dict[str, Any] = json.loads(
    """{
  "customer_id": "customer_id",
  "order_id": "order_id",
  "tenant_id": "tenant_id"
}"""
) or {}

_ENV_OVERRIDES: Dict[str, Any] = json.loads(
    """{
  "api_key": null,
  "webhook_secret": null
}"""
) or {}

SNIPPETS: list[Dict[str, Any]] = json.loads(
    """[
  {
    "description": "Adds exponential backoff helpers for resilient retry logic.",
    "file": "snippets/enhanced-retries.yaml",
    "name": "enhanced-retries"
  },
  {
    "description": "Registers webhook handlers for Stripe customer portal events.",
    "file": "snippets/customer-portal-webhook.yaml",
    "name": "customer-portal-webhook"
  }
]"""
) or []

ENVIRONMENT_SNAPSHOT = {
    "has_api_key": bool(_ENV_OVERRIDES.get("api_key")),
    "has_webhook_secret": bool(_ENV_OVERRIDES.get("webhook_secret")),
}


@dataclass(slots=True)
class StripePaymentConfig:
    """Runtime configuration for Stripe Payment."""

    enabled: bool = bool(DEFAULTS.get("enabled", True))
    metadata: Dict[str, Any] = field(
        default_factory=lambda: dict(DEFAULTS.get("metadata", {}))
    )


class StripePayment:
    """Primary facade exposing Stripe Payment capabilities."""

    def __init__(self, config: StripePaymentConfig | None = None) -> None:
        self.config = config or StripePaymentConfig()

    def health_check(self) -> Dict[str, Any]:
        """Return module health metadata with Stripe-focused diagnostics."""

        status = "ok" if self.config.enabled else "degraded"
        return {
            "module": MODULE_NAME,
            "status": status,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "mode": str(DEFAULTS.get("mode", "test")),
            "default_currency": str(DEFAULTS.get("default_currency", "usd")),
            "automatic_payment_methods": bool(
                DEFAULTS.get("automatic_payment_methods", True)
            ),
            "webhook_enabled": bool(WEBHOOK.get("enabled", True)),
            "manual_capture_available": _resolve_bool(
                FEATURE_FLAGS.get("allow_manual_capture"), True
            ),
        }

    def metadata(self) -> Dict[str, Any]:
        """Return runtime metadata for diagnostics and discovery."""

        defaults = _clone(DEFAULTS) or {}
        config_snapshot = _clone(DEFAULTS) or {}
        config_snapshot["enabled"] = self.config.enabled
        config_snapshot["metadata"] = dict(self.config.metadata)

        return {
            "module": MODULE_NAME,
            "title": MODULE_TITLE,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "defaults": defaults,
            "config": config_snapshot,
            "retry_policy": _clone(RETRY_POLICY) or {},
            "webhook": _clone_webhook(),
            "features": _normalize_feature_flags(FEATURE_FLAGS),
            "billing": _clone(BILLING) or {},
            "network": _clone(NETWORK) or {},
            "metadata_keys": _clone(METADATA_KEYS) or {},
            "environment": dict(ENVIRONMENT_SNAPSHOT),
            "snippets": _clone(SNIPPETS) or [],
        }

    def retry_policy(self) -> Dict[str, Any]:
        """Return a defensive copy of the retry policy settings."""

        return _clone(RETRY_POLICY) or {}

    def webhook_config(self) -> Dict[str, Any]:
        """Return the configured webhook settings."""

        return _clone_webhook()

    def allowed_currencies(self) -> list[str]:
        """Return the list of allowed currencies."""

        return _sanitize_string_list(BILLING.get("allowed_currencies"))

    def payment_method_types(self) -> list[str]:
        """Return the default payment method types."""

        return _sanitize_string_list(
            BILLING.get("default_payment_method_types")
        )

    def environment_snapshot(self) -> Dict[str, Any]:
        """Return a copy of the environment snapshot."""

        return dict(ENVIRONMENT_SNAPSHOT)


def _clone(payload: Any) -> Any:
    return json.loads(json.dumps(payload))


def _clone_webhook() -> Dict[str, Any]:
    webhook = _clone(WEBHOOK) or {}
    events = webhook.get("events") or []
    webhook["events"] = [
        str(event).strip() for event in events if str(event).strip()
    ]
    return webhook


def _normalize_feature_flags(flags: Dict[str, Any]) -> Dict[str, bool]:
    snapshot: Dict[str, bool] = {}
    for key, value in (flags or {}).items():
        snapshot[key] = _resolve_bool(value, False)
    return snapshot


def _sanitize_string_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(item).strip() for item in values if str(item).strip()]


def _resolve_bool(value: Any, fallback: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value > 0
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    return fallback


__all__ = [
    "StripePayment",
    "StripePaymentConfig",
    "ENVIRONMENT_SNAPSHOT",
    "MODULE_NAME",
    "MODULE_TITLE",
]
