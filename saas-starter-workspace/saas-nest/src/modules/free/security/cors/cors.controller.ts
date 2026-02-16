import { Controller, Get } from "@nestjs/common";

import {
  CorsService,
  CorsMetadataPayload,
  CORS_FEATURES,
} from "./cors.service";

@Controller("security/cors")
export class CorsController {
  constructor(private readonly corsService: CorsService) { }

  @Get("metadata")
  getMetadata(): CorsMetadataPayload {
    return this.corsService.getMetadata();
  }

  @Get("features")
  listFeatures(): { features: string[] } {
    return { features: [...CORS_FEATURES] };
  }

}
