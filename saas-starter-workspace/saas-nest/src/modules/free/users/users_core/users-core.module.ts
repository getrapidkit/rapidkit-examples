import { Module } from "@nestjs/common";

import { UsersCoreController } from "./users-core.controller";
import { UsersCoreService } from "./users-core.service";

@Module({
  controllers: [UsersCoreController],
  providers: [UsersCoreService],
  exports: [UsersCoreService],
})
export class UsersCoreModule {}
