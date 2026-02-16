import { Module } from "@nestjs/common";
import { ConfigModule } from "@nestjs/config";

import oauthConfiguration from "./configuration";
import { OauthController } from "./oauth.controller";
import { OauthService } from "./oauth.service";
import { OauthHealthController } from "../../../../health/oauth.health";

@Module({
  imports: [ConfigModule.forFeature(oauthConfiguration)],
  controllers: [OauthController, OauthHealthController],
  providers: [OauthService],
  exports: [OauthService],
})
export class OauthModule { }
