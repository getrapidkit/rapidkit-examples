import { Module } from "@nestjs/common";
import { ConfigModule } from "@nestjs/config";

import { SettingsController } from "./settings.controller";
import { SettingsHealthController } from "../../../../health/settings.health";
import { SettingsService } from "./settings.service";

@Module({
  imports: [ConfigModule],
  controllers: [SettingsController, SettingsHealthController],
  providers: [SettingsService],
  exports: [SettingsService],
})
export class SettingsModule {}
