"""Shared type definitions for API Keys."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Iterable, List, Mapping, Protocol, Sequence

UTC = timezone.utc


class ApiKeysStatus(str, Enum):
    """Possible lifecycle states for an API key."""

    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass(slots=True)
class ApiKeysConfig:
    """Runtime configuration for API Keys."""

    enabled: bool = True
    key_prefix: str = "rk"
    display_prefix: str = "rk_live_"
    token_separator: str = "."  # noqa: S105
    secret_bytes: int = 32
    prefix_bytes: int = 6
    prefix_charset: str = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    hash_algorithm: str = "sha256"
    pepper_env: str = "RAPIDKIT_API_KEYS_PEPPER"
    pepper: str | None = None
    default_scopes: tuple[str, ...] = ("read",)
    allowed_scopes: tuple[str, ...] | None = None
    allow_scope_wildcards: bool = False
    ttl_hours: int | None = None
    rotation_days: int = 90
    max_active_per_owner: int = 25
    leak_window_hours: int = 72
    metadata: Dict[str, Any] = field(default_factory=dict)
    repository_backend: str = "memory"
    persist_last_used: bool = True
    audit_trail: bool = True
    features: tuple[str, ...] = (
        "deterministic_hashing",
        "scope_enforcement",
        "usage_metrics",
        "rotation_window",
        "leak_detection",
    )


@dataclass(slots=True)
class ApiKeysAuditEntry:
    """Represents an audit log entry for key operations."""

    event: str
    key_id: str
    owner_id: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ApiKeysRecord:
    """Represents a persisted API key."""

    key_id: str
    owner_id: str
    prefix: str
    hashed_key: str
    scopes: tuple[str, ...]
    label: str | None
    created_at: datetime
    expires_at: datetime | None
    revoked_at: datetime | None = None
    last_used_at: datetime | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_active(self, *, now: datetime | None = None) -> bool:
        """Return True when this key is active and not expired."""

        if self.revoked_at is not None:
            return False
        if self.expires_at is None:
            return True
        reference = now or datetime.now(tz=UTC)
        return reference < self.expires_at

    def status(self, *, now: datetime | None = None) -> ApiKeysStatus:
        """Return the lifecycle status for the key."""

        if self.revoked_at is not None:
            return ApiKeysStatus.REVOKED
        reference = now or datetime.now(tz=UTC)
        if self.expires_at is not None and reference >= self.expires_at:
            return ApiKeysStatus.EXPIRED
        return ApiKeysStatus.ACTIVE


@dataclass(slots=True)
class ApiKeysIssueResult:
    """Return payload when issuing a key."""

    token: str
    secret: str
    record: ApiKeysRecord


@dataclass(slots=True)
class ApiKeysVerification:
    """Result payload from verifying an API key."""

    record: ApiKeysRecord | None
    scopes_granted: tuple[str, ...]
    required_scopes: tuple[str, ...]
    matched: bool
    reason: str | None = None


@dataclass(slots=True)
class ApiKeysHealth:
    """Health payload describing repository state."""

    status: str
    totals: Dict[str, int] = field(default_factory=dict)
    rotation_due: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ApiKeysTelemetry:
    """Simple telemetry bundle for reporting usage information."""

    issued: int
    verified: int
    revoked: int
    failures: Dict[str, int] = field(default_factory=dict)


class ApiKeysRepository(Protocol):
    """Repository contract for storing API keys."""

    def persist(self, record: ApiKeysRecord) -> None: ...

    def update(self, record: ApiKeysRecord) -> None: ...

    def delete(self, key_id: str) -> None: ...

    def get_by_id(self, key_id: str) -> ApiKeysRecord | None: ...

    def get_by_prefix(self, prefix: str) -> ApiKeysRecord | None: ...

    def list_for_owner(
        self,
        owner_id: str,
        *,
        include_inactive: bool = False,
    ) -> List[ApiKeysRecord]: ...

    def stats(self) -> Dict[str, int]: ...

    def load_recent(self, *, limit: int = 20) -> Sequence[ApiKeysRecord]: ...

    def count_active_for_owner(self, owner_id: str) -> int: ...

    def audit(self, entry: ApiKeysAuditEntry) -> None: ...


class ApiKeysAuditSink(Protocol):
    """Hook for persisting audit events."""

    def write(self, entry: ApiKeysAuditEntry) -> None: ...


def summarise_scopes(scopes: Iterable[str]) -> tuple[str, ...]:
    """Normalise and deduplicate the provided scopes."""

    cleaned: list[str] = []
    for scope in scopes:
        candidate = scope.strip()
        if not candidate:
            continue
        cleaned.append(candidate)
    return tuple(dict.fromkeys(cleaned))


__all__ = [
    "ApiKeysStatus",
    "ApiKeysConfig",
    "ApiKeysAuditEntry",
    "ApiKeysRecord",
    "ApiKeysIssueResult",
    "ApiKeysVerification",
    "ApiKeysHealth",
    "ApiKeysTelemetry",
    "ApiKeysRepository",
    "ApiKeysAuditSink",
    "summarise_scopes",
]
