"""Runtime facade for the API Keys module."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import uuid
from collections import Counter, defaultdict
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from threading import RLock
from typing import Any, Callable, Dict, Iterable, Mapping, MutableMapping, Sequence

from .api_keys_health import build_health_payload
from .api_keys_types import (
    ApiKeysAuditEntry,
    ApiKeysAuditSink,
    ApiKeysConfig,
    ApiKeysIssueResult,
    ApiKeysRecord,
    ApiKeysRepository,
    ApiKeysStatus,
    ApiKeysTelemetry,
    ApiKeysVerification,
    summarise_scopes,
)

MODULE_NAME = "api_keys"
MODULE_TITLE = "API Keys"
MODULE_VERSION = "0.1.0"
MODULE_TIER = "free"

UTC = timezone.utc

DEFAULTS: Dict[str, Any] = json.loads(
    """{
  "allow_scope_wildcards": false,
  "allowed_scopes": [
    "read",
    "write",
    "admin"
  ],
  "audit_trail": true,
  "default_scopes": [
    "read"
  ],
  "display_prefix": "rk_live_",
  "hash_algorithm": "sha256",
  "key_prefix": "rk",
  "leak_window_hours": 72,
  "max_active_per_owner": 25,
  "pepper_env": "RAPIDKIT_API_KEYS_PEPPER",
  "persist_last_used": true,
  "prefix_bytes": 6,
  "prefix_charset": "ABCDEFGHJKLMNPQRSTUVWXYZ23456789",
  "rotation_days": 90,
  "secret_bytes": 32,
  "token_separator": ".",
  "ttl_hours": null
}"""
)

FEATURE_FLAGS: tuple[str, ...] = tuple(sorted(DEFAULTS.get("features", [])))
DEFAULT_HASH_ITERATIONS = 390_000
DEFAULT_HASH_SALT = b"rapidkit-api-keys"


class ApiKeysError(Exception):
    """Base error for Api Keys runtime."""


class ApiKeysConfigurationError(ApiKeysError):
    """Raised when configuration values are invalid."""


class ApiKeysRepositoryError(ApiKeysError):
    """Raised when repository interactions fail."""


class ApiKeysVerificationError(ApiKeysError):
    """Raised when token verification fails due to malformed inputs."""


class ApiKeysRateLimitError(ApiKeysError):
    """Raised when issuance quotas are exceeded."""


def _now() -> datetime:
    return datetime.now(tz=UTC)


def _normalise_config(config: Mapping[str, Any] | ApiKeysConfig | None) -> ApiKeysConfig:
    if config is None:
        return ApiKeysConfig(**DEFAULTS)
    if isinstance(config, ApiKeysConfig):
        return config
    merged = dict(DEFAULTS)
    merged.update(dict(config))
    return ApiKeysConfig(**merged)


def _derive_pepper(config: ApiKeysConfig) -> str:
    if config.pepper:
        return config.pepper
    candidate = os.getenv(config.pepper_env, "").strip()
    if candidate:
        return candidate
    return ""


def _pbkdf2(secret: str, *, pepper: str, algorithm: str) -> str:
    if not pepper:
        raise ApiKeysConfigurationError(
            "Pepper must be configured via config.pepper or environment variable."
        )
    digest = hashlib.pbkdf2_hmac(
        algorithm,
        secret.encode("utf-8"),
        (pepper + MODULE_NAME).encode("utf-8") + DEFAULT_HASH_SALT,
        DEFAULT_HASH_ITERATIONS,
        dklen=64,
    )
    return base64.urlsafe_b64encode(digest).decode("ascii")


def _mask_secret(secret: str) -> str:
    visible = secret[:4]
    return f"{visible}***"


class InMemoryApiKeysRepository(ApiKeysRepository):
    """Thread-safe in-memory repository suitable for defaults and testing."""

    def __init__(self) -> None:
        self._records: Dict[str, ApiKeysRecord] = {}
        self._prefix_index: Dict[str, str] = {}
        self._audit_log: list[ApiKeysAuditEntry] = []
        self._lock = RLock()

    def persist(self, record: ApiKeysRecord) -> None:
        with self._lock:
            if record.key_id in self._records:
                raise ApiKeysRepositoryError(
                    f"Api key '{record.key_id}' already exists."
                )
            self._records[record.key_id] = record
            self._prefix_index[record.prefix] = record.key_id

    def update(self, record: ApiKeysRecord) -> None:
        with self._lock:
            if record.key_id not in self._records:
                raise ApiKeysRepositoryError(
                    f"Api key '{record.key_id}' cannot be updated because it does not exist."
                )
            self._records[record.key_id] = record
            self._prefix_index[record.prefix] = record.key_id

    def delete(self, key_id: str) -> None:
        with self._lock:
            record = self._records.pop(key_id, None)
            if record:
                self._prefix_index.pop(record.prefix, None)

    def get_by_id(self, key_id: str) -> ApiKeysRecord | None:
        with self._lock:
            return self._records.get(key_id)

    def get_by_prefix(self, prefix: str) -> ApiKeysRecord | None:
        with self._lock:
            key_id = self._prefix_index.get(prefix)
            if key_id is None:
                return None
            return self._records.get(key_id)

    def list_for_owner(
        self,
        owner_id: str,
        *,
        include_inactive: bool = False,
    ) -> list[ApiKeysRecord]:
        with self._lock:
            values = [record for record in self._records.values() if record.owner_id == owner_id]
        if include_inactive:
            return sorted(values, key=lambda item: item.created_at, reverse=True)
        return [record for record in values if record.is_active()]

    def stats(self) -> Dict[str, int]:
        totals = Counter()
        with self._lock:
            records = list(self._records.values())
        now = _now()
        for record in records:
            totals[record.status(now=now).value] += 1
        totals["total"] = len(records)
        return dict(totals)

    def load_recent(self, *, limit: int = 20) -> Sequence[ApiKeysRecord]:
        with self._lock:
            records = sorted(self._records.values(), key=lambda item: item.created_at, reverse=True)
        return records[: max(limit, 0)]

    def count_active_for_owner(self, owner_id: str) -> int:
        return sum(1 for record in self.list_for_owner(owner_id) if record.is_active())

    def audit(self, entry: ApiKeysAuditEntry) -> None:
        with self._lock:
            self._audit_log.append(entry)

    @property
    def audit_log(self) -> list[ApiKeysAuditEntry]:
        with self._lock:
            return list(self._audit_log)


class ApiKeys:
    """Primary facade exposing API Keys capabilities."""

    def __init__(
        self,
        config: Mapping[str, Any] | ApiKeysConfig | None = None,
        *,
        repository: ApiKeysRepository | None = None,
        audit_sink: ApiKeysAuditSink | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.config = _normalise_config(config)
        self.repository = repository or InMemoryApiKeysRepository()
        self.audit_sink = audit_sink
        self._pepper = _derive_pepper(self.config)
        self._clock = clock or _now
        self._telemetry = ApiKeysTelemetry(issued=0, verified=0, revoked=0)
        self._failure_counters: MutableMapping[str, int] = defaultdict(int)

    # ------------------------------------------------------------------
    # Issuance
    # ------------------------------------------------------------------
    def issue_key(
        self,
        owner_id: str,
        *,
        scopes: Iterable[str] | None = None,
        label: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        ttl_hours: int | None = None,
    ) -> ApiKeysIssueResult:
        if not owner_id or not owner_id.strip():
            raise ApiKeysConfigurationError("owner_id must be provided")
        if not self.config.enabled:
            raise ApiKeysConfigurationError("Api Keys module is disabled")

        candidate_scopes = summarise_scopes(scopes or self.config.default_scopes)
        self._validate_scopes(candidate_scopes)

        active_count = self.repository.count_active_for_owner(owner_id)
        if self.config.max_active_per_owner and active_count >= self.config.max_active_per_owner:
            raise ApiKeysRateLimitError(
                f"Owner '{owner_id}' has reached the active key limit ({self.config.max_active_per_owner})."
            )

        prefix = self._generate_prefix()
        secret = self._generate_secret()
        hashed_secret = _pbkdf2(secret, pepper=self._pepper, algorithm=self.config.hash_algorithm)

        now = self._clock()
        ttl = ttl_hours if ttl_hours is not None else self.config.ttl_hours
        expires_at = now + timedelta(hours=ttl) if ttl else None

        record_metadata = {
            "label": label or "",
            "module": MODULE_NAME,
            "version": MODULE_VERSION,
        }
        if metadata:
            record_metadata.update(dict(metadata))

        record = ApiKeysRecord(
            key_id=str(uuid.uuid4()),
            owner_id=owner_id,
            prefix=prefix,
            hashed_key=hashed_secret,
            scopes=candidate_scopes,
            label=label,
            created_at=now,
            expires_at=expires_at,
            metadata=record_metadata,
        )

        self.repository.persist(record)
        self._telemetry.issued += 1
        self._write_audit("issue", record, extra={"label": label})

        token = f"{prefix}{self.config.token_separator}{secret}"
        return ApiKeysIssueResult(token=token, secret=secret, record=record)

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------
    def verify_token(
        self,
        token: str,
        *,
        required_scopes: Iterable[str] | None = None,
        touch_last_used: bool | None = None,
    ) -> ApiKeysVerification:
        if not token or self.config.token_separator not in token:
            raise ApiKeysVerificationError("Token format invalid")

        prefix, secret = self._split_token(token)
        record = self.repository.get_by_prefix(prefix)
        candidate_required = summarise_scopes(required_scopes or [])

        if record is None:
            self._register_failure("not_found")
            return ApiKeysVerification(
                record=None,
                scopes_granted=tuple(),
                required_scopes=candidate_required,
                matched=False,
                reason="not_found",
            )

        now = self._clock()
        if not record.is_active(now=now):
            status = record.status(now=now)
            self._register_failure(status.value)
            return ApiKeysVerification(
                record=record,
                scopes_granted=tuple(),
                required_scopes=candidate_required,
                matched=False,
                reason=status.value,
            )

        hashed_secret = _pbkdf2(secret, pepper=self._pepper, algorithm=self.config.hash_algorithm)
        if not hmac.compare_digest(hashed_secret, record.hashed_key):
            self._register_failure("credentials_mismatch")
            return ApiKeysVerification(
                record=None,
                scopes_granted=tuple(),
                required_scopes=candidate_required,
                matched=False,
                reason="credentials_mismatch",
            )

        granted = self._resolve_scope_grants(candidate_required, record.scopes)
        matched = len(granted) == len(candidate_required)

        if matched and (touch_last_used if touch_last_used is not None else self.config.persist_last_used):
            updated = replace(record, last_used_at=now)
            self.repository.update(updated)
            record = updated

        self._telemetry.verified += 1
        self._write_audit("verify", record, extra={"granted": granted})

        if not matched:
            self._register_failure("scope_mismatch")

        return ApiKeysVerification(
            record=record,
            scopes_granted=granted,
            required_scopes=candidate_required,
            matched=matched,
            reason=None if matched else "scope_mismatch",
        )

    # ------------------------------------------------------------------
    # Revocation
    # ------------------------------------------------------------------
    def revoke_key(self, key_id: str, *, reason: str | None = None) -> ApiKeysRecord:
        record = self.repository.get_by_id(key_id)
        if record is None:
            raise ApiKeysRepositoryError(
                f"Cannot revoke key '{key_id}' because it does not exist."
            )
        if record.revoked_at is not None:
            return record

        now = self._clock()
        metadata = dict(record.metadata)
        if reason:
            metadata.setdefault("revocation_reasons", []).append(reason)
        updated = replace(record, revoked_at=now, metadata=metadata)
        self.repository.update(updated)
        self._telemetry.revoked += 1
        self._write_audit("revoke", updated, extra={"reason": reason})
        return updated

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------
    def list_keys(self, owner_id: str, *, include_inactive: bool = False) -> list[ApiKeysRecord]:
        return self.repository.list_for_owner(owner_id, include_inactive=include_inactive)

    def health_check(self) -> dict[str, Any]:
        stats = self.repository.stats()
        recent = self.repository.load_recent(limit=20)
        pepper_loaded = bool(self._pepper)
        payload = build_health_payload(
            config=self.config,
            stats=stats,
            recent_records=recent,
            metadata={
                "module": MODULE_NAME,
                "version": MODULE_VERSION,
                "tier": MODULE_TIER,
                "features": FEATURE_FLAGS,
            },
            pepper_loaded=pepper_loaded,
            issues=self._health_issues(pepper_loaded=pepper_loaded),
            now=self._clock(),
        )
        payload.setdefault("telemetry", {})
        payload["telemetry"].update(
            {
                "issued": self._telemetry.issued,
                "verified": self._telemetry.verified,
                "revoked": self._telemetry.revoked,
                "failures": dict(self._failure_counters),
            }
        )
        return payload

    def metadata(self) -> Dict[str, Any]:
        return {
            "module": MODULE_NAME,
            "title": MODULE_TITLE,
            "version": MODULE_VERSION,
            "tier": MODULE_TIER,
            "features": FEATURE_FLAGS,
            "config": {
                "rotation_days": self.config.rotation_days,
                "ttl_hours": self.config.ttl_hours,
                "max_active_per_owner": self.config.max_active_per_owner,
                "repository_backend": self.config.repository_backend,
            },
        }

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------
    def _health_issues(self, *, pepper_loaded: bool) -> list[str]:
        issues: list[str] = []
        if not self.config.enabled:
            issues.append("module_disabled")
        if not pepper_loaded:
            issues.append("pepper_missing")
        if self.config.rotation_days <= 0:
            issues.append("rotation_disabled")
        if self.config.max_active_per_owner <= 0:
            issues.append("active_limit_disabled")
        return issues

    def _generate_prefix(self) -> str:
        alphabet = self.config.prefix_charset
        if len(alphabet) < 4:
            raise ApiKeysConfigurationError("prefix_charset must contain at least 4 characters")
        body = "".join(secrets.choice(alphabet) for _ in range(max(self.config.prefix_bytes, 1)))
        return f"{self.config.display_prefix}{body.lower()}"

    def _generate_secret(self) -> str:
        entropy = secrets.token_bytes(max(self.config.secret_bytes, 16))
        return base64.urlsafe_b64encode(entropy).rstrip(b"=").decode("ascii")

    def _split_token(self, token: str) -> tuple[str, str]:
        prefix, secret = token.split(self.config.token_separator, 1)
        if not prefix or not secret:
            raise ApiKeysVerificationError("Token missing prefix or secret component")
        return prefix, secret

    def _validate_scopes(self, candidate_scopes: tuple[str, ...]) -> None:
        if not candidate_scopes:
            raise ApiKeysConfigurationError("At least one scope must be requested")
        allowed = self.config.allowed_scopes
        if allowed is None:
            return
        allowed_set = set(allowed)
        if self.config.allow_scope_wildcards:
            allowed_wildcards = {scope.split("*", 1)[0] for scope in allowed if "*" in scope}
        else:
            allowed_wildcards = set()
        for scope in candidate_scopes:
            if scope in allowed_set:
                continue
            if self.config.allow_scope_wildcards and any(scope.startswith(prefix) for prefix in allowed_wildcards):
                continue
            raise ApiKeysConfigurationError(f"Scope '{scope}' is not permitted")

    def _resolve_scope_grants(
        self, required_scopes: tuple[str, ...], granted_scopes: tuple[str, ...]
    ) -> tuple[str, ...]:
        if not required_scopes:
            return tuple(granted_scopes)
        granted = []
        for required in required_scopes:
            if required in granted_scopes:
                granted.append(required)
                continue
            if "*" in granted_scopes and self.config.allow_scope_wildcards:
                granted.append(required)
                continue
            wildcard_matches = [scope for scope in granted_scopes if scope.endswith("*")]
            if any(required.startswith(scope.rstrip("*")) for scope in wildcard_matches):
                granted.append(required)
        return tuple(granted)

    def _write_audit(
        self,
        event: str,
        record: ApiKeysRecord,
        *,
        extra: Mapping[str, Any] | None = None,
    ) -> None:
        if not self.config.audit_trail and self.audit_sink is None:
            return
        entry = ApiKeysAuditEntry(
            event=event,
            key_id=record.key_id,
            owner_id=record.owner_id,
            timestamp=self._clock(),
            metadata={
                "scopes": list(record.scopes),
                "label": record.label,
                "token_prefix": record.prefix,
                "module": MODULE_NAME,
                "version": MODULE_VERSION,
                "extra": dict(extra or {}),
            },
        )
        if self.config.audit_trail:
            try:
                self.repository.audit(entry)
            except AttributeError:
                pass
        if self.audit_sink is not None:
            self.audit_sink.write(entry)

    def _register_failure(self, category: str) -> None:
        self._failure_counters[category] += 1


def create_runtime(
    config: Mapping[str, Any] | ApiKeysConfig | None = None,
    *,
    repository: ApiKeysRepository | None = None,
    audit_sink: ApiKeysAuditSink | None = None,
) -> ApiKeys:
    """Return a freshly initialised runtime."""

    return ApiKeys(config=config, repository=repository, audit_sink=audit_sink)


@lru_cache(maxsize=1)
def _cached_runtime() -> ApiKeys:
    return ApiKeys()


def get_api_keys_runtime(
    config: Mapping[str, Any] | ApiKeysConfig | None = None,
    *,
    repository: ApiKeysRepository | None = None,
    audit_sink: ApiKeysAuditSink | None = None,
) -> ApiKeys:
    """Return a cached runtime unless explicit dependencies are provided."""

    if config is not None or repository is not None or audit_sink is not None:
        return ApiKeys(config=config, repository=repository, audit_sink=audit_sink)
    return _cached_runtime()


def reset_runtime_cache() -> None:
    """Clear any cached runtime instance."""

    _cached_runtime.cache_clear()  # type: ignore[attr-defined]


__all__ = [
    "ApiKeys",
    "ApiKeysError",
    "ApiKeysConfigurationError",
    "ApiKeysRepositoryError",
    "ApiKeysVerificationError",
    "ApiKeysRateLimitError",
    "InMemoryApiKeysRepository",
    "create_runtime",
    "get_api_keys_runtime",
    "reset_runtime_cache",
]
