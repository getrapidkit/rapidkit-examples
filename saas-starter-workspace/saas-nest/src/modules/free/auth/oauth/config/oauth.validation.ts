import * as Joi from "joi";

export const oauthValidationSchema = Joi.object({
  OAUTH_REDIRECT_BASE_URL: Joi.string()
    .uri({ allowRelative: false })
    .default("https://example.com/oauth"),
  OAUTH_STATE_TTL_SECONDS: Joi.number()
    .integer()
    .min(1)
    .default(300),
  OAUTH_STATE_CLEANUP_INTERVAL: Joi.number()
    .integer()
    .min(1)
    .default(60),
  OAUTH_PROVIDERS: Joi.string().optional(),
});
