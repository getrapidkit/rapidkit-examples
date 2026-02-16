import { Test, TestingModule } from "@nestjs/testing";

import { RedisController } from "../../../../../src/modules/free/cache/redis/redis.controller";
import { RedisHealthController } from "../../../../../src/health/redis.health";
import { RedisModule } from "../../../../../src/modules/free/cache/redis/redis.module";
import { RedisService } from "../../../../../src/modules/free/cache/redis/redis.service";

jest.mock("ioredis", () => {
  return jest.fn().mockImplementation(() => ({
    status: "ready",
    options: { host: "localhost", port: 6379 },
    connect: jest.fn().mockResolvedValue(undefined),
    ping: jest.fn().mockResolvedValue("PONG"),
    quit: jest.fn().mockResolvedValue(undefined),
    disconnect: jest.fn(),
  }));
});

describe("Redis NestJS Integration", () => {
  let controller: RedisController;
  let healthController: RedisHealthController;
  let service: RedisService;

  beforeAll(async () => {
    const moduleRef: TestingModule = await Test.createTestingModule({
      imports: [RedisModule],
    }).compile();

    controller = moduleRef.get(RedisController);
    healthController = moduleRef.get(RedisHealthController);
    service = moduleRef.get(RedisService);
  });

  afterAll(async () => {
    await service.close();
  });

  it("should describe cache metadata", () => {
    const metadata = controller.getMetadata();

    expect(metadata.module).toBe("redis");
    expect(metadata.retry.preconnect).toBeDefined();
  });

  it("should expose ping payload", async () => {
    const payload = await controller.ping();

    expect(payload.status).toBe("ok");
    expect(payload.result).toBe("PONG");
  });

  it("should expose health payload", async () => {
    const payload = await healthController.getModuleHealth();

    expect(payload.status).toBe("ok");
    expect(payload.module).toBe("redis");
    expect(payload.checks.connection).toBe(true);
  });

  it("should describe client", async () => {
    const description = await controller.getClient();

    expect(description.status).toBeDefined();
    expect(description.client_repr).toContain("Redis");
  });
});
