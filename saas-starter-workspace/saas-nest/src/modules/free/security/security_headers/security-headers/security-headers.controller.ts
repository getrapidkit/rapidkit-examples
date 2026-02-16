import { Controller, Get } from "@nestjs/common";

import { SecurityHeadersService } from "./security-headers.service";

@Controller("security-headers")
export class SecurityHeadersController {
  constructor(private readonly service: SecurityHeadersService) { }

  @Get("headers")
  headers(): Record<string, string> {
    return this.service.getHeaders();
  }
}
