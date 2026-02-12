import { DynamicModule, Module } from "@nestjs/common";
import { AiAssistantController } from "./ai_assistant.controller";
import {
    AI_ASSISTANT_CONFIG,
    AiAssistantModuleConfig,
    AiAssistantService,
    defaultAiAssistantConfig,
} from "./ai_assistant.service";

function buildConfig(overrides?: Partial<AiAssistantModuleConfig>): AiAssistantModuleConfig {
    return {
        ...defaultAiAssistantConfig(),
        ...overrides,
        providers: overrides?.providers?.length ? overrides.providers : defaultAiAssistantConfig().providers,
    };
}

@Module({
    controllers: [AiAssistantController],
    providers: [
        {
            provide: AI_ASSISTANT_CONFIG,
            useFactory: () => defaultAiAssistantConfig(),
        },
        AiAssistantService,
    ],
    exports: [AiAssistantService],
})
export class AiAssistantModule {
    static forRoot(config?: Partial<AiAssistantModuleConfig>): DynamicModule {
        return {
            module: AiAssistantModule,
            controllers: [AiAssistantController],
            providers: [
                {
                    provide: AI_ASSISTANT_CONFIG,
                    useValue: buildConfig(config),
                },
                AiAssistantService,
            ],
            exports: [AiAssistantService],
        };
    }
}
