import {
  Controller,
  Get,
  HttpCode,
  HttpStatus,
  Logger,
  ServiceUnavailableException,
} from '@nestjs/common';

import {
  DB_REDIS_VENDOR_MODULE,
  type RedisClientDescription,
  type RedisMetadata,
  type RedisPingPayload,
  RedisService,
} from './redis.service';

@Controller('redis')
export class RedisController {
  private readonly logger = new Logger(RedisController.name);

  constructor(private readonly service: RedisService) {}

  @Get('metadata')
  getMetadata(): RedisMetadata {
    return this.service.describeCache();
  }

  @Get('ping')
  @HttpCode(HttpStatus.OK)
  async ping(): Promise<RedisPingPayload> {
    try {
      const payload = await this.service.ping();
      this.logger.debug(`Redis ping payload=${JSON.stringify(payload)}`);
      return payload;
    } catch (error) {
      const detail =
        error instanceof Error && error.message
          ? error.message
          : String(error);
      this.logger.error(`Redis ping failed: ${detail}`);
      throw new ServiceUnavailableException({
        status: 'error',
        module: DB_REDIS_VENDOR_MODULE,
        detail,
      });
    }
  }

  @Get('client')
  async getClient(): Promise<RedisClientDescription> {
    try {
      return await this.service.describeClient();
    } catch (error) {
      const detail =
        error instanceof Error && error.message
          ? error.message
          : String(error);
      this.logger.error(`Redis client inspection failed: ${detail}`);
      throw new ServiceUnavailableException({
        status: 'error',
        module: DB_REDIS_VENDOR_MODULE,
        detail,
      });
    }
  }
}
