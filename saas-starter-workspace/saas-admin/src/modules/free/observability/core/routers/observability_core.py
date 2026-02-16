"""FastAPI route definitions for Observability Core."""

from __future__ import annotations

from typing import Mapping

from fastapi import APIRouter, Response

from ..observability_core import ObservabilityCore, ObservabilityCoreConfig, get_runtime
from ..observability_core_types import (
    ObservabilityEvent,
    ObservabilityEventCreate,
    ObservabilityMetricSnapshot,
    ObservabilitySpan,
    ObservabilitySummary,
)


def _runtime(config: ObservabilityCoreConfig | None) -> ObservabilityCore:
    return get_runtime(config, refresh=config is not None)


def build_router(config: ObservabilityCoreConfig | Mapping[str, object] | None = None) -> APIRouter:
    router = APIRouter(prefix="/observability-core", tags=["Observability Core"])
    runtime_config: ObservabilityCoreConfig | None
    if isinstance(config, Mapping):
        runtime_config = ObservabilityCoreConfig.from_mapping(config)
    else:
        runtime_config = config

    facade = _runtime(runtime_config)

    @router.get("/health", summary="Observability Core health check", response_model=ObservabilitySummary)
    async def read_health() -> ObservabilitySummary:
        return ObservabilitySummary(**facade.health_check())

    @router.get("/metrics", summary="Rendered metrics payload", response_model=ObservabilityMetricSnapshot)
    async def read_metrics() -> ObservabilityMetricSnapshot:
        return facade.export_metrics_snapshot()

    @router.get("/metrics/raw", summary="Raw metrics exposition", response_class=Response)
    async def read_raw_metrics() -> Response:
        payload, content_type = facade.export_metrics()
        return Response(content=payload, media_type=content_type)

    @router.get("/events", summary="Recent observability events", response_model=list[ObservabilityEvent])
    async def read_events(limit: int = 50) -> list[ObservabilityEvent]:
        events = facade.recent_events(limit)
        return [ObservabilityEvent(**event) for event in events]

    @router.post("/events", summary="Emit a transient observability event", response_model=ObservabilityEvent)
    async def create_event(payload: ObservabilityEventCreate) -> ObservabilityEvent:
        event = facade.emit_event(
            payload.name,
            severity=payload.severity,
            attributes=payload.attributes,
        )
        return ObservabilityEvent(**event)

    @router.get("/traces", summary="Recent captured spans", response_model=list[ObservabilitySpan])
    async def read_spans(limit: int = 25) -> list[ObservabilitySpan]:
        spans = facade.recent_spans(limit)
        return [ObservabilitySpan(**span) for span in spans]

    return router
