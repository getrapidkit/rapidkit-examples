"""Shared type definitions for Stripe Payment."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class StripePaymentResult:
    """Standard result envelope for Stripe Payment operations."""

    success: bool
    message: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)

