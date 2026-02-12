"""Module bootstrap namespace."""

from src.modules.free.essentials.settings import (
    BaseSettings,
    CustomConfigSource,
    Field,
    Settings,
    configure_fastapi_app,
    get_settings,
    settings,
    settings_dependency,
)
import src.modules.free.essentials.logging
import src.modules.free.essentials.deployment
import src.modules.free.essentials.middleware
import src.modules.free.ai.ai_assistant
# <<<inject:module-init>>>