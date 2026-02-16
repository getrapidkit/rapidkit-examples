import {
  Controller,
  Get,
  HttpCode,
  HttpStatus,
  Logger,
  ServiceUnavailableException,
} from '@nestjs/common';
import { hostname } from 'node:os';

import { SecurityHeadersService } from '../modules/free/security/security_headers/security-headers/security-headers.service';

@Controller('api/health/module')
export class SecurityHeadersHealthController {
  private readonly logger = new Logger(SecurityHeadersHealthController.name);

  constructor(private readonly securityHeadersService: SecurityHeadersService) {}

  @Get('security-headers')
  @HttpCode(HttpStatus.OK)
  getModuleHealth(): Record<string, unknown> {
    try {
      const payload = this.securityHeadersService.health();
      return {
        ...payload,
        hostname: hostname(),
      };
    } catch (error) {
      const detail = error instanceof Error && error.message ? error.message : 'security headers health check failed';
      this.logger.error(`Security headers health check failed: ${detail}`);
      throw new ServiceUnavailableException({
        status: 'error',
        module: "security_headers",
        detail,
      });
    }
  }
}
