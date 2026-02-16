/** Health controller for the Authentication Core NestJS integration. */

import {
  Controller,
  Get,
  HttpCode,
  HttpStatus,
  Logger,
  ServiceUnavailableException,
} from "@nestjs/common";

import { AuthCoreHealthPayload, AuthCoreService } from "../modules/free/auth/core/auth-core.service";

@Controller("api/health/module")
export class AuthCoreHealthController {
  private readonly logger = new Logger(AuthCoreHealthController.name);

  constructor(private readonly service: AuthCoreService) {}

  @Get("auth-core")
  @HttpCode(HttpStatus.OK)
  getModuleHealth(): AuthCoreHealthPayload {
    try {
      const payload = this.service.health();
      this.logger.debug(`auth-core health payload=${JSON.stringify(payload)}`);
      return payload;
    } catch (error) {
      const detail =
        error instanceof Error && error.message
          ? error.message
          : "auth-core health check failed";
      this.logger.error(`auth-core health check failed: ${detail}`);
      throw new ServiceUnavailableException({
        status: "error",
        module: "auth_core",
        detail,
      });
    }
  }
}
