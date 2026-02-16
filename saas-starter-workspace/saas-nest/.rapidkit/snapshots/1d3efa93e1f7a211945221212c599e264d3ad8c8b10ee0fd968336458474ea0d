import { Controller, Get, Param } from "@nestjs/common";

import { OauthService } from "./oauth.service";

@Controller("oauth")
export class OauthController {
  constructor(private readonly service: OauthService) {}

  @Get("metadata")
  getMetadata(): Record<string, unknown> {
    return this.service.describe();
  }

  @Get("features")
  getFeatures(): { features: string[] } {
    return { features: this.service.listFeatures() };
  }

  @Get("providers")
  listProviders(): Record<string, unknown> {
    return this.service.listProviders();
  }

  @Get("providers/:provider")
  getProvider(@Param("provider") provider: string): Record<string, unknown> {
    const runtimeProvider = this.service.getProviderStrict(provider);
    return {
      name: runtimeProvider.name,
      authorizeUrl: runtimeProvider.authorizeUrl,
      tokenUrl: runtimeProvider.tokenUrl,
      scopes: [...runtimeProvider.scopes],
      userinfoUrl: runtimeProvider.userinfoUrl,
      redirectUri: runtimeProvider.redirectUri,
    };
  }
}
