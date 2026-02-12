import { registerAs } from "@nestjs/config";
import { AiAssistantModuleConfig, defaultAiAssistantConfig } from "./ai_assistant.service";

export const configuration = registerAs(
    "ai_assistant",
    (): AiAssistantModuleConfig => defaultAiAssistantConfig(),
);
