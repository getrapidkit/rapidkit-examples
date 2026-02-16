"""Configuration primitives for the application layer."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AppConfig:
    """Application-level configuration aggregated from RapidKit settings."""

    environment: str = "development"
    service_name: str = "saas-admin"


__all__ = ["AppConfig"]