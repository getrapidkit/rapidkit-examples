import { Test } from "@nestjs/testing";
import { AiAssistantController } from "../../src/modules/free/ai/ai_assistant/ai_assistant.controller";
import {
  AI_ASSISTANT_CONFIG,
  AiAssistantService,
  defaultAiAssistantConfig,
} from "../../src/modules/free/ai/ai_assistant/ai_assistant.service";

describe("AiAssistantController", () => {
  let controller: AiAssistantController;

  beforeEach(async () => {
    const moduleRef = await Test.createTestingModule({
      controllers: [AiAssistantController],
      providers: [
        AiAssistantService,
        {
          provide: AI_ASSISTANT_CONFIG,
          useValue: defaultAiAssistantConfig(),
        },
      ],
    }).compile();

    controller = moduleRef.get(AiAssistantController);
  });

  it("creates a completion", async () => {
    const response = await controller.createCompletion({ prompt: "hello" });
    expect(response.content).toContain("hello");
    expect(response.provider).toBeDefined();
  });

  it("lists providers", () => {
    expect(controller.listProviders()).toContain("echo");
  });

  it("returns health snapshot", () => {
    const health = controller.getHealth();
    expect(health.module).toBe("ai_assistant");
    expect(health.status).toBe("ok");
  });
});
