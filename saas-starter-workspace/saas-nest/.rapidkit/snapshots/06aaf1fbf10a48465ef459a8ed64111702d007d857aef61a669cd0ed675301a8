import { Module } from "@nestjs/common";
import { ConfigModule } from "@nestjs/config";

import corsConfiguration from "./cors.configuration";
import { CorsController } from "./cors.controller";
import { CorsHealthController } from "../../../../health/cors.health";
import { CorsService } from "./cors.service";

@Module({
  imports: [ConfigModule.forFeature(corsConfiguration)],
  controllers: [CorsController, CorsHealthController],
  providers: [CorsService],
  exports: [CorsService],
})
export class CorsModule {}
