import { Module } from '@nestjs/common';

import { DatabasePostgresModule } from '../modules/free/database/db_postgres/postgres.module';
import { DatabasePostgresHealthController } from './postgres-health.controller';

@Module({
  imports: [DatabasePostgresModule],
  controllers: [DatabasePostgresHealthController],
})
export class DatabasePostgresHealthModule {}
