import {
  Controller,
  Get,
  HttpCode,
  HttpStatus,
  Logger,
  ServiceUnavailableException,
} from '@nestjs/common';
import { hostname } from 'node:os';

import { DatabasePostgresService } from '../modules/free/database/db_postgres/postgres.service';

@Controller('api/health/module')
export class DatabasePostgresHealthController {
  private readonly logger = new Logger(DatabasePostgresHealthController.name);

  constructor(private readonly postgresService: DatabasePostgresService) {}

  @Get('postgres')
  @HttpCode(HttpStatus.OK)
  async getPostgresHealth(): Promise<Record<string, unknown>> {
    try {
      await this.postgresService.checkHealth();
      const pool = await this.postgresService.getPoolStatus();
      const payload = {
        status: 'ok',
        module: 'db_postgres',
        url: this.postgresService.getDatabaseUrl(true),
        hostname: hostname(),
        pool,
      };
      this.logger.debug(`PostgreSQL health payload=${JSON.stringify(payload)}`);
      return payload;
    } catch (error) {
      const message =
        error instanceof Error && error.message
          ? error.message
          : 'postgres health check failed';
      this.logger.error(`PostgreSQL health check failed: ${message}`);
      throw new ServiceUnavailableException({
        status: 'error',
        module: 'db_postgres',
        detail: message,
      });
    }
  }
}
