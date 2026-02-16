import * as Joi from "joi";

export const redisValidationSchema = Joi.object({
  REDIS_URL: Joi.string().uri().optional(),
  REDIS_HOST: Joi.string().default("localhost"),
  REDIS_PORT: Joi.number().integer().min(1).default(6379),
  REDIS_DB: Joi.number().integer().min(0).default(0),
  REDIS_PASSWORD: Joi.string().allow("").default(""),
  REDIS_USE_TLS: Joi.boolean()
    .truthy("true")
    .truthy("1")
    .truthy("yes")
    .truthy("on")
    .falsy("false")
    .falsy("0")
    .falsy("no")
    .falsy("off")
    .default(false),
  REDIS_PRECONNECT: Joi.boolean()
    .truthy("true")
    .truthy("1")
    .truthy("yes")
    .truthy("on")
    .falsy("false")
    .falsy("0")
    .falsy("no")
    .falsy("off")
    .default(false),
  REDIS_CONNECT_RETRIES: Joi.number()
    .integer()
    .min(0)
    .default(3),
  REDIS_CONNECT_BACKOFF_BASE: Joi.number()
    .min(0)
    .default(0.5),
  CACHE_TTL: Joi.number().integer().min(0).default(3600),
});
