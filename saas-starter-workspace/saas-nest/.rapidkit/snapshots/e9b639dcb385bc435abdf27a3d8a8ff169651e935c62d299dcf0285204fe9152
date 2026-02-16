import { Controller, Get } from "@nestjs/common";

import { SecurityHeadersService } from "./security-headers.service";

@Controller("security-headers")
export class SecurityHeadersController {
  constructor(private readonly service: SecurityHeadersService) {}

  @Get("health")
  health(): Record<string, unknown> {
    return this.service.health();
  }

  @Get("headers")
  headers(): Record<string, string> {
    return this.service.getHeaders();
  }
}
