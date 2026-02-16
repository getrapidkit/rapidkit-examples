/* eslint-disable @typescript-eslint/no-var-requires, @typescript-eslint/no-require-imports, global-require */

import type { DynamicModule, Type } from '@nestjs/common';

// Central export for dynamically injected RapidKit modules

type ModuleRef = DynamicModule | Type<unknown>;

const registerOptionalModule = (loader: () => ModuleRef | null | undefined): ModuleRef | null => {
	try {
		const resolved = loader();
		return resolved ?? null;
	} catch {
		return null;
	}
};

const optionalModules: Array<ModuleRef | null> = [
	registerOptionalModule(() => require('../config/logging.module').LoggingModule as ModuleRef),
	registerOptionalModule(() => require('../config/settings.module').SettingsModule as ModuleRef),
	registerOptionalModule(() => require('../deployment/deployment.module').DeploymentModule as ModuleRef),
	registerOptionalModule(() => require('./free/auth/core').AuthCoreModule.forRoot() as ModuleRef),
	registerOptionalModule(() => require('./free/auth/oauth').OauthModule as ModuleRef),
	registerOptionalModule(() => require('./free/users/users_core').UsersCoreModule as ModuleRef),
	registerOptionalModule(() => require('../health/users-core-health.module').UsersCoreHealthModule as ModuleRef),
	registerOptionalModule(() => require('./free/cache/redis').RedisModule as ModuleRef),
	registerOptionalModule(() => require('./free/database/db_postgres/postgres.module').DatabasePostgresModule as ModuleRef),
	registerOptionalModule(() => require('../health/postgres-health.module').DatabasePostgresHealthModule as ModuleRef),
	registerOptionalModule(() => require('./free/security/cors/cors.module').CorsModule as ModuleRef),
	registerOptionalModule(() => require('./free/security/rate_limiting/rate-limiting.module').RateLimitingModule as ModuleRef),
	registerOptionalModule(() => require('../health/rate-limiting-health.module').RateLimitingHealthModule as ModuleRef),
	registerOptionalModule(() => require('./free/security/security_headers/security-headers/security-headers.module').SecurityHeadersModule.register() as ModuleRef),
	registerOptionalModule(() => require('../health/security-headers-health.module').SecurityHeadersHealthModule as ModuleRef),
	// <<<inject:module-exports>>>
];

export const rapidkitModules: ModuleRef[] = optionalModules.filter(Boolean) as ModuleRef[];
