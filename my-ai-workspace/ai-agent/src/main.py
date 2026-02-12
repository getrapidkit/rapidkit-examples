"""ai-agent application entrypoint."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import os

import yaml
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.agents.support_agent import SupportAgent
from src.modules.free.ai.ai_assistant.routers.ai.ai_assistant import (
    register_ai_assistant,
)
from src.modules.free.ai.ai_assistant.providers.openai_provider import OpenAIProvider

# <<<inject:imports>>>

try:
    # canonical health package
    from src.health import register_health_routes as _core_register_health_routes
except ImportError:  # pragma: no cover - health package not generated yet

    def _register_health_routes(_: FastAPI) -> None:
        return None

else:

    def _register_health_routes(app: FastAPI) -> None:
        try:
            _core_register_health_routes(app)
        except Exception:  # pragma: no cover - defensive best-effort registration
            return None


from .routing import api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Coordinate startup/shutdown hooks contributed by RapidKit modules."""

    _ = app  # ensure the app reference stays available for injected hooks
    # <<<inject:startup>>>
    try:
        yield
    finally:
        # <<<inject:shutdown>>>
        pass


# Load config from YAML
with open("config/ai_assistant.yaml") as f:
    config_data = yaml.safe_load(f)

app = FastAPI(
    title="AI Agent API",
    version="1.0.0",
    description="Production AI Assistant powered by RapidKit",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register AI Assistant
assistant = register_ai_assistant(app, config=config_data)

# Optional: register OpenAI provider when API key is available
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    openai_provider = OpenAIProvider(
        name="openai",
        api_key=openai_api_key,
        model="gpt-4",
        temperature=0.7,
    )
    assistant.register_provider(openai_provider)

app.include_router(api_router, prefix="/api")
# Expose module-provided health routers under /api/health/module/*
_register_health_routes(app)
# <<<inject:routes>>>


@app.get("/")
async def root():
    return {
        "message": "AI Agent API is running",
        "endpoints": {
            "completions": "/ai/assistant/completions",
            "stream": "/ai/assistant/stream",
            "providers": "/ai/assistant/providers",
            "health": "/ai/assistant/health",
        },
    }


@app.post("/support/ticket")
async def handle_support_ticket(
    message: str,
    request: Request,
) -> dict[str, object]:
    assistant_runtime = request.app.state.ai_assistant
    agent = SupportAgent(assistant_runtime)

    provider_name = "openai"
    if "openai" not in assistant_runtime.list_providers():
        provider_name = "support" if "support" in assistant_runtime.list_providers() else "echo"

    urgency_response = assistant_runtime.chat(
        f"Classify urgency (low/medium/high): {message}",
        provider=provider_name,
        settings={"temperature": 0.1},
    )
    urgency = urgency_response.content.strip().lower()
    if "high" in urgency:
        normalized_urgency = "high"
    elif "medium" in urgency:
        normalized_urgency = "medium"
    else:
        normalized_urgency = "low"

    if provider_name == "openai":
        response = agent.handle_ticket(message)
    else:
        response = assistant_runtime.chat(message, provider=provider_name)

    return {
        "ticket_id": "TKT-12345",
        "urgency": normalized_urgency,
        "ai_response": response.content,
        "latency_ms": response.latency_ms,
        "next_action": "escalate" if normalized_urgency == "high" else "monitor",
        "provider": provider_name,
    }
# <<<inject:routes>>>