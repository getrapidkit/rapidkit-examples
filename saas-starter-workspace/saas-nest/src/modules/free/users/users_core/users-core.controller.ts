import { Controller, Get } from "@nestjs/common";

import {
  UsersCoreFeature,
  UsersCoreMetadata,
  UsersCoreService,
} from "./users-core.service";

@Controller("users-core")
export class UsersCoreController {
  constructor(private readonly service: UsersCoreService) { }

  @Get("metadata")
  getMetadata(): UsersCoreMetadata {
    return this.service.buildMetadata();
  }

  @Get("features")
  listFeatures(): { features: UsersCoreFeature[] } {
    return { features: this.service.listFeatures() };
  }

}
