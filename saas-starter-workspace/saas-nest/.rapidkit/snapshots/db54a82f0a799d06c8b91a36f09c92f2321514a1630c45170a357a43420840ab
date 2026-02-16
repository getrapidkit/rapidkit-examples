import { Module } from '@nestjs/common';

import { SecurityHeadersModule } from '../modules/free/security/security_headers/security-headers/security-headers.module';
import { SecurityHeadersHealthController } from './security-headers-health.controller';

@Module({
  imports: [SecurityHeadersModule],
  controllers: [SecurityHeadersHealthController],
})
export class SecurityHeadersHealthModule {}
