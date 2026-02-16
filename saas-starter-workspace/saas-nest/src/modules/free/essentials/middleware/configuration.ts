import { registerAs } from '@nestjs/config';

export interface MiddlewareConfiguration {
  enabled: boolean;
  processTimeHeader: boolean;
  serviceHeader: boolean;
  serviceHeaderName: string;
  serviceName: string | null;
  customHeaders: boolean;
  customHeaderName: string;
  customHeaderValue: string;
  corsEnabled: boolean;
  corsAllowOrigins: string[];
  corsAllowMethods: string[];
  corsAllowHeaders: string[];
  corsAllowCredentials: boolean;
  metadata: Record<string, unknown>;
}

export default registerAs('middleware', (): MiddlewareConfiguration => ({
  enabled: true,
  processTimeHeader: true,
  serviceHeader: true,
  serviceHeaderName: "X-Service",
  serviceName: null,
  customHeaders: true,
  customHeaderName: "X-Custom-Header",
  customHeaderValue: "RapidKit",
  corsEnabled: false,
  corsAllowOrigins: [
  "*"
],
  corsAllowMethods: [
  "*"
],
  corsAllowHeaders: [
  "*"
],
  corsAllowCredentials: true,
  metadata: {},
}));
