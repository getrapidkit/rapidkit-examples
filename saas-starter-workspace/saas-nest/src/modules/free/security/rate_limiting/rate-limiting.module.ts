import { Global, Module } from "@nestjs/common";
import { ConfigModule } from "@nestjs/config";

import { RateLimitingController } from "./rate-limiting.controller";
import { RateLimitingService } from "./rate-limiting.service";
import { RateLimitingGuard } from "./rate-limiting.guard";
import { rateLimitingConfiguration } from "./rate-limiting.configuration";

export const RATE_LIMITING_CONFIG_NAMESPACE = "rate-limiting";

@Global()
@Module({
  imports: [ConfigModule.forFeature(rateLimitingConfiguration)],
  controllers: [RateLimitingController],
  providers: [RateLimitingService, RateLimitingGuard],
  exports: [RateLimitingService, RateLimitingGuard],
})
export class RateLimitingModule {}
