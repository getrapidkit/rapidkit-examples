import { Controller, Get } from "@nestjs/common";

import {
  UsersCoreHealthPayload,
  UsersCoreFeature,
  UsersCoreMetadata,
  UsersCoreService,
} from "./users-core.service";

@Controller("users-core")
export class UsersCoreController {
  constructor(private readonly service: UsersCoreService) {}

  @Get("metadata")
  getMetadata(): UsersCoreMetadata {
    return this.service.buildMetadata();
  }

  @Get("features")
  listFeatures(): { features: UsersCoreFeature[] } {
    return { features: this.service.listFeatures() };
  }

  @Get("health")
  async getHealth(): Promise<UsersCoreHealthPayload> {
    return this.service.resolveHealth();
  }
}
