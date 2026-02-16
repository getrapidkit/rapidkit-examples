"use strict";

const DEFAULTS = {
  "hash_name": "sha256",
  "issuer": "RapidKit",
  "iterations": 390000,
  "pepper_env": "RAPIDKIT_AUTH_CORE_PEPPER",
  "policy": {
    "min_length": 12,
    "require_digits": true,
    "require_lowercase": true,
    "require_symbols": false,
    "require_uppercase": true
  },
  "salt_bytes": 32,
  "token_bytes": 32,
  "token_ttl_seconds": 1800
};

function loadConfiguration() {
  return {
    module: "auth_core",
    issuer: DEFAULTS.issuer,
    hashName: DEFAULTS.hash_name,
    iterations: DEFAULTS.iterations,
    saltBytes: DEFAULTS.salt_bytes,
    tokenBytes: DEFAULTS.token_bytes,
    tokenTtlSeconds: DEFAULTS.token_ttl_seconds,
    pepperEnv: DEFAULTS.pepper_env,
    policy: DEFAULTS.policy,
  };
}

module.exports = {
  loadConfiguration,
  DEFAULTS,
};
