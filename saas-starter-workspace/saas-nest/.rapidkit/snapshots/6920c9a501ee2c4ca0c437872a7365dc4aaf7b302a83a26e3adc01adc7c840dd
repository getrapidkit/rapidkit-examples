import { registerAs } from "@nestjs/config";

export type RedisConfiguration = {
  url: string;
  preconnect: boolean;
  retries: number;
  backoffBase: number;
  ttl: number;
};

const TRUTHY = ["1", "true", "yes", "on"];

const toBoolean = (value: string | undefined, fallback: boolean): boolean => {
  if (!value) {
    return fallback;
  }
  return TRUTHY.includes(value.toLowerCase());
};

const toNumber = (value: string | undefined, fallback: number): number => {
  if (!value) {
    return fallback;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
};

const buildUrl = (): string => {
  const direct = process.env.REDIS_URL;
  if (direct && direct.length > 0) {
    return direct;
  }

  const host = process.env.REDIS_HOST ?? "localhost";
  const port = process.env.REDIS_PORT ?? 6379;
  const db = process.env.REDIS_DB ?? 0;
  const password =
    process.env.REDIS_PASSWORD ?? "";
  const useTls = toBoolean(
    process.env.REDIS_USE_TLS,
    false
  );
  const scheme = useTls ? "rediss" : "redis";
  const auth = password ? `:${password}@` : "";
  return `${scheme}://${auth}${host}:${port}/${db}`;
};

export default registerAs("redis", (): RedisConfiguration => ({
  url: buildUrl(),
  preconnect: toBoolean(
    process.env.REDIS_PRECONNECT,
    false
  ),
  retries: toNumber(
    process.env.REDIS_CONNECT_RETRIES,
    3
  ),
  backoffBase: toNumber(
    process.env.REDIS_CONNECT_BACKOFF_BASE,
    0.5
  ),
  ttl: toNumber(process.env.CACHE_TTL, 3600),
}));
