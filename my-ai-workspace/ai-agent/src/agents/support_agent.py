"""Customer support AI agent."""

from __future__ import annotations

from collections.abc import Sequence

from src.modules.free.ai.ai_assistant.ai_assistant import AiAssistant
from src.modules.free.ai.ai_assistant.ai_assistant_types import AssistantMessage, AssistantResponse


class SupportAgent:
    """AI-powered customer support agent."""

    def __init__(self, assistant: AiAssistant) -> None:
        self._assistant = assistant
        self._system_prompt = (
            "You are a helpful customer support agent. "
            "Be concise, friendly, and solution-oriented. "
            "If you don't know the answer, escalate to human support."
        )

    def handle_ticket(
        self,
        customer_message: str,
        ticket_history: Sequence[AssistantMessage] | None = None,
    ) -> AssistantResponse:
        context = [AssistantMessage(role="system", content=self._system_prompt)]
        if ticket_history:
            context.extend(ticket_history)

        return self._assistant.chat(
            customer_message,
            provider="openai",
            context=context,
        )

    def classify_urgency(self, message: str) -> str:
        prompt = f"Classify urgency (low/medium/high): {message}"
        response = self._assistant.chat(
            prompt,
            provider="openai",
            settings={"temperature": 0.1},
        )
        value = response.content.strip().lower()
        if "high" in value:
            return "high"
        if "medium" in value:
            return "medium"
        return "low"
