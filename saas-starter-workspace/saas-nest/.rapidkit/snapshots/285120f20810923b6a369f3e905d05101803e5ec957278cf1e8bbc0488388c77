import { registerAs } from "@nestjs/config";

type RawOauthProvider = Record<string, unknown>;

type OauthConfiguration = {
  redirectBaseUrl: string;
  stateTtlSeconds: number;
  stateCleanupInterval: number;
  providers: Record<string, RawOauthProvider>;
};

type DefaultOauthConfig = {
  redirect_base_url?: string;
  state_ttl_seconds?: number;
  state_cleanup_interval?: number;
  providers?: Record<string, RawOauthProvider>;
};

const DEFAULTS: DefaultOauthConfig = {
  "providers": {
    "github": {
      "authorize_url": "https://github.com/login/oauth/authorize",
      "client_id_env": "GITHUB_OAUTH_CLIENT_ID",
      "client_secret_env": "GITHUB_OAUTH_CLIENT_SECRET",
      "scopes": [
        "read:user",
        "user:email"
      ],
      "token_url": "https://github.com/login/oauth/access_token",
      "userinfo_url": "https://api.github.com/user"
    },
    "google": {
      "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
      "client_id_env": "GOOGLE_OAUTH_CLIENT_ID",
      "client_secret_env": "GOOGLE_OAUTH_CLIENT_SECRET",
      "scopes": [
        "openid",
        "email",
        "profile"
      ],
      "token_url": "https://oauth2.googleapis.com/token",
      "userinfo_url": "https://openidconnect.googleapis.com/v1/userinfo"
    }
  },
  "redirect_base_url": "https://example.com/oauth",
  "state_cleanup_interval": 60,
  "state_ttl_seconds": 300
};

const parseInteger = (value: string | undefined, fallback: number): number => {
  if (typeof value !== "string" || value.trim().length === 0) {
    return fallback;
  }
  const parsed = Number.parseInt(value, 10);
  return Number.isFinite(parsed) ? parsed : fallback;
};

const parseProviders = (value: string | undefined, fallback: Record<string, RawOauthProvider>): Record<string, RawOauthProvider> => {
  if (typeof value !== "string" || value.trim().length === 0) {
    return fallback;
  }
  try {
    const parsed = JSON.parse(value);
    if (parsed && typeof parsed === "object") {
      return parsed as Record<string, RawOauthProvider>;
    }
  } catch {
    // ignore malformed overrides and fall back to defaults
  }
  return fallback;
};

export default registerAs("oauth", (): OauthConfiguration => {
  const rawProviders = DEFAULTS.providers ?? {};
  return {
    redirectBaseUrl:
      process.env.OAUTH_REDIRECT_BASE_URL ?? (DEFAULTS.redirect_base_url ?? "https://example.com/oauth"),
    stateTtlSeconds: parseInteger(
      process.env.OAUTH_STATE_TTL_SECONDS,
      DEFAULTS.state_ttl_seconds ?? 300,
    ),
    stateCleanupInterval: parseInteger(
      process.env.OAUTH_STATE_CLEANUP_INTERVAL,
      DEFAULTS.state_cleanup_interval ?? 60,
    ),
    providers: parseProviders(process.env.OAUTH_PROVIDERS, rawProviders),
  };
});
