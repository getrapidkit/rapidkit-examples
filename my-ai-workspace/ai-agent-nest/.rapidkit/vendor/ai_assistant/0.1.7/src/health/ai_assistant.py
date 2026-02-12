"""Health helpers for the Ai Assistant runtime."""

from __future__ import annotations

import sys
from types import ModuleType
from typing import Any, Mapping

try:
    from ..ai_assistant import AiAssistant, AiAssistantConfig  # type: ignore[import]
except ImportError:  # pragma: no cover - fallback for isolated execution
    # Pick the *most recently loaded* module that provides the expected symbols.
    # This avoids nondeterminism when multiple modules in sys.modules expose the
    # same attribute names (common in test environments).
    _runtime_module: ModuleType | None = next(
        (
            module
            for module in reversed(list(sys.modules.values()))
            if isinstance(module, ModuleType)
            and hasattr(module, "AiAssistant")
            and hasattr(module, "AiAssistantConfig")
        ),
        None,
    )
    if _runtime_module is None:  # pragma: no cover - defensive guard
        raise

    AiAssistant = getattr(_runtime_module, "AiAssistant")  # type: ignore[assignment]
    AiAssistantConfig = getattr(_runtime_module, "AiAssistantConfig")  # type: ignore[assignment]


def check_health(
    config: AiAssistantConfig | None = None,
    *,
    context: Mapping[str, Any] | None = None,
) -> Mapping[str, Any]:
    """Return a detailed health payload for the assistant runtime."""

    assistant = AiAssistant(config or AiAssistantConfig())
    report = assistant.health_report()

    if context:
        enriched = dict(report)
        enriched.setdefault("metadata", {}).update(dict(context))
        return enriched
    return report


__all__ = ["check_health"]
