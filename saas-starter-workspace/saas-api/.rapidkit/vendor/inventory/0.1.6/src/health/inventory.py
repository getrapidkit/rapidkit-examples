"""Health helpers for Inventory."""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

from src.modules.free.billing.inventory.inventory import InventoryService
from src.modules.free.billing.inventory.types.inventory import utc_now


def build_health_payload(
    *,
    service: Optional[InventoryService] = None,
    extra: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Return a structured health payload for the inventory module."""

    inventory_service = service or InventoryService()
    payload = inventory_service.health_check()
    payload.setdefault("checked_at", utc_now().isoformat())
    if extra:
        payload.setdefault("metadata", {}).update(dict(extra))
    return payload


def health_status(service: Optional[InventoryService] = None) -> str:
    """Convenience wrapper returning the aggregate health status."""

    return build_health_payload(service=service)["status"]
