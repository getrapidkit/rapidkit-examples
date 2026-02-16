import { Controller, Get, HttpCode, HttpStatus, Logger } from "@nestjs/common";
import { hostname } from "node:os";

import { USERS_CORE_CONFIGURATION_NAMESPACE } from "../modules/free/users/users_core/users-core.configuration";
import { UsersCoreService } from "../modules/free/users/users_core/users-core.service";

@Controller("api/health/module")
export class UsersCoreHealthController {
  private readonly logger = new Logger(UsersCoreHealthController.name);

  constructor(private readonly usersCoreService: UsersCoreService) {}

  @Get("users-core")
  @HttpCode(HttpStatus.OK)
  async getModuleHealth(): Promise<Record<string, unknown>> {
    try {
      const snapshot = await this.usersCoreService.resolveHealth();
      const status = typeof snapshot?.status === "string" ? snapshot.status : "unknown";

      return {
        module: "users_core",
        namespace: USERS_CORE_CONFIGURATION_NAMESPACE,
        hostname: hostname(),
        checkedAt: new Date().toISOString(),
        status,
        details: snapshot,
      };
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      this.logger.error(`Users Core health check failed: ${message}`);
      return {
        module: "users_core",
        namespace: USERS_CORE_CONFIGURATION_NAMESPACE,
        hostname: hostname(),
        checkedAt: new Date().toISOString(),
        status: "error",
        details: {
          error: message,
        },
      };
    }
  }
}
