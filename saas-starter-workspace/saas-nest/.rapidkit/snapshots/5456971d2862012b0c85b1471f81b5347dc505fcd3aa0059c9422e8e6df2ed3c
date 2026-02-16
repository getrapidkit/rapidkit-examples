import { DynamicModule, Module } from "@nestjs/common";

import { SecurityHeadersController } from "./security-headers.controller";
import {
  SecurityHeadersOptions,
  SecurityHeadersService,
} from "./security-headers.service";

export const SECURITY_HEADERS_OPTIONS_TOKEN = "SECURITY_HEADERS_OPTIONS";

@Module({
  controllers: [SecurityHeadersController],
  providers: [
    {
      provide: SECURITY_HEADERS_OPTIONS_TOKEN,
      useValue: undefined,
    },
    {
      provide: SecurityHeadersService,
      useFactory: (options?: Partial<SecurityHeadersOptions> | null) =>
        new SecurityHeadersService(options ?? undefined),
      inject: [SECURITY_HEADERS_OPTIONS_TOKEN],
    },
  ],
  exports: [SecurityHeadersService],
})
export class SecurityHeadersModule {
  static register(
    options?: Partial<SecurityHeadersOptions>,
  ): DynamicModule {
    return {
      module: SecurityHeadersModule,
      providers: [
        {
          provide: SECURITY_HEADERS_OPTIONS_TOKEN,
          useValue: options ?? undefined,
        },
      ],
      exports: [SecurityHeadersService],
    };
  }
}
