import { Controller, Get, HttpCode, HttpStatus } from "@nestjs/common";

import { RedisService, RedisHealthPayload } from "../modules/free/cache/redis/redis.service";

@Controller("api/health/module")
export class RedisHealthController {
  constructor(private readonly service: RedisService) {}

  @Get("redis")
  @HttpCode(HttpStatus.OK)
  async getModuleHealth(): Promise<RedisHealthPayload> {
    return this.service.getHealthPayload();
  }
}
