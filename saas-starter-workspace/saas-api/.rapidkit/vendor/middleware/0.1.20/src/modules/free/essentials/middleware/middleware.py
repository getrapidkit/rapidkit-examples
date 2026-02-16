from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


@dataclass
class MiddlewareConfig:
    """Runtime configuration for Middleware."""

    enabled: bool = True
    cors_enabled: bool = False
    cors_allow_origins: List[str] = field(default_factory=lambda: ["*"])
    cors_allow_methods: List[str] = field(default_factory=lambda: ["*"])
    cors_allow_headers: List[str] = field(default_factory=lambda: ["*"])
    cors_allow_credentials: bool = True
    process_time_header: bool = True
    service_header: bool = True
    service_name: str | None = None
    service_header_name: str = "X-Service"
    custom_headers: bool = True
    custom_header_name: str = "X-Powered-By"
    custom_header_value: str = "RapidKit"
    metadata: Dict[str, Any] = field(default_factory=dict)
    extra_factories: List[Callable[..., Any]] = field(default_factory=list)


def build_default_config() -> MiddlewareConfig:
    """Return default configuration payload."""

    return MiddlewareConfig()
