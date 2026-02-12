"""OpenAI provider implementation."""

from __future__ import annotations

import os
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from openai import OpenAI

from src.modules.free.ai.ai_assistant.ai_assistant_types import AssistantMessage, ProviderStatus


class OpenAIProvider:
    """OpenAI chat completion provider."""

    def __init__(
        self,
        *,
        name: str = "openai",
        api_key: str | None = None,
        model: str = "gpt-4",
        temperature: float = 0.7,
    ) -> None:
        self.name = name
        self._model = model
        self._temperature = temperature
        self._client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self._last_latency_ms: float | None = None

    def generate(
        self,
        prompt: str,
        *,
        conversation: Sequence[AssistantMessage],
        settings: Mapping[str, Any] | None = None,
    ) -> str:
        messages = [{"role": msg.role, "content": msg.content} for msg in conversation]
        messages.append({"role": "user", "content": prompt})

        response = self._client.chat.completions.create(
            model=settings.get("model", self._model) if settings else self._model,
            messages=messages,
            temperature=settings.get("temperature", self._temperature) if settings else self._temperature,
        )

        return response.choices[0].message.content or ""

    def stream(
        self,
        prompt: str,
        *,
        conversation: Sequence[AssistantMessage],
        settings: Mapping[str, Any] | None = None,
    ) -> Iterable[str]:
        messages = [{"role": msg.role, "content": msg.content} for msg in conversation]
        messages.append({"role": "user", "content": prompt})

        stream = self._client.chat.completions.create(
            model=settings.get("model", self._model) if settings else self._model,
            messages=messages,
            temperature=settings.get("temperature", self._temperature) if settings else self._temperature,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def note_latency(self, latency_ms: float) -> None:
        self._last_latency_ms = latency_ms

    def health(self) -> ProviderStatus:
        return ProviderStatus(
            name=self.name,
            status="ok",
            latency_ms=self._last_latency_ms,
            details={"model": self._model, "temperature": self._temperature},
        )
