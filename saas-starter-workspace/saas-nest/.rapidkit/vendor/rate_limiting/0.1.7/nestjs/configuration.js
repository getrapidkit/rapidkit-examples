"use strict";

const defaults = {"backend": "memory", "default_block_seconds": null, "default_limit": 120, "default_priority": 100, "default_rule_name": "default", "default_scope": "identity", "default_window": 60, "enabled": true, "forwarded_for_header": "X-Forwarded-For", "headers": {"limit": "X-RateLimit-Limit", "remaining": "X-RateLimit-Remaining", "reset": "X-RateLimit-Reset", "retry_after": "Retry-After", "rule": "X-RateLimit-Rule"}, "identity_header": "X-RateLimit-Identity", "metadata": {}, "redis_prefix": "rate-limit", "redis_url": "", "rules": [], "trust_forwarded_for": false};
const rules = defaults.rules ?? [];
const headers = defaults.headers ?? {};

function loadConfiguration() {
  return {
    module: "rate_limiting",
    title: "Rate Limiting",
    enabled: defaults.enabled ?? true,
    backend: defaults.backend ?? "memory",
    redisUrl: defaults.redis_url ?? "redis://localhost:6379/2",
    redisPrefix: defaults.redis_prefix ?? "rate-limit",
    forwardedForHeader: defaults.forwarded_for_header ?? "X-Forwarded-For",
    identityHeader: defaults.identity_header ?? "X-RateLimit-Identity",
    defaultRule: {
      name: defaults.default_rule_name ?? "default",
      limit: defaults.default_limit ?? 120,
      windowSeconds: defaults.default_window ?? 60,
      scope: defaults.default_scope ?? "identity",
      priority: defaults.default_priority ?? 100,
      blockSeconds: defaults.default_block_seconds ?? null,
    },
    rules,
    headers: {
      limit: headers.limit ?? "X-RateLimit-Limit",
      remaining: headers.remaining ?? "X-RateLimit-Remaining",
      reset: headers.reset ?? "X-RateLimit-Reset",
      retryAfter: headers.retry_after ?? "Retry-After",
      rule: headers.rule ?? "X-RateLimit-Rule",
    },
  };
}

module.exports = {
  loadConfiguration,
};
