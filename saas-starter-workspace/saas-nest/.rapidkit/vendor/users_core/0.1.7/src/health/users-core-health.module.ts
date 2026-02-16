import { Module } from "@nestjs/common";

import { UsersCoreModule } from "../modules/free/users/users_core/users-core.module";
import { UsersCoreHealthController } from "./users-core-health.controller";

@Module({
  imports: [UsersCoreModule],
  controllers: [UsersCoreHealthController],
})
export class UsersCoreHealthModule {}
