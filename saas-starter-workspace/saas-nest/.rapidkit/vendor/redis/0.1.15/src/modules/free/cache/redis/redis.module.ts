import { Module } from "@nestjs/common";
import { ConfigModule } from "@nestjs/config";

import redisConfiguration from "./configuration";
import { RedisService } from "./redis.service";
import { RedisController } from "./redis.controller";
import { RedisHealthController } from "../../../../health/redis.health";

@Module({
  imports: [ConfigModule.forFeature(redisConfiguration)],
  controllers: [RedisController, RedisHealthController],
  providers: [RedisService],
  exports: [RedisService],
})
export class RedisModule {}
