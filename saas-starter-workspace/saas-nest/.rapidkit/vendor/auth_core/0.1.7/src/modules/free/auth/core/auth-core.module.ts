import { DynamicModule, Module, Provider } from "@nestjs/common";
import { ConfigModule, ConfigType } from "@nestjs/config";

import { AUTH_CORE_CONFIG, AuthCoreConfig, AuthCoreService, AuthCorePolicy } from "./auth-core.service";

export const AUTH_CORE_CONFIGURATION = "AUTH_CORE_CONFIGURATION";

const DEFAULTS: AuthCoreConfig = {
  hashName: "sha256",
  iterations: 390000,
  saltBytes: 32,
  tokenBytes: 32,
  tokenTtlSeconds: 1800,
  pepperEnv: "RAPIDKIT_AUTH_CORE_PEPPER",
  issuer: "RapidKit",
  policy: {
    minLength: 12,
    requireUppercase: true,
    requireLowercase: true,
    requireDigits: true,
    requireSymbols: false,
  } as AuthCorePolicy,
};

@Module({})
export class AuthCoreModule {
  static forRoot(config: Partial<AuthCoreConfig> = {}): DynamicModule {
    const merged: AuthCoreConfig = {
      ...DEFAULTS,
      ...config,
      policy: {
        ...DEFAULTS.policy,
        ...(config.policy ?? {}),
      },
    };

    const providers: Provider[] = [
      {
        provide: AUTH_CORE_CONFIG,
        useValue: merged,
      },
      AuthCoreService,
    ];

    return {
      module: AuthCoreModule,
      global: true,
      imports: [ConfigModule],
      providers,
      exports: [AUTH_CORE_CONFIG, AuthCoreService],
    };
  }

  static forConfig(configuration: ConfigType<typeof authCoreConfiguration>): DynamicModule {
    return AuthCoreModule.forRoot(configuration);
  }
}

export function authCoreConfiguration(): AuthCoreConfig {
  return DEFAULTS;
}
