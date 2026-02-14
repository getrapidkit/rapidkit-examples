"use strict";

function loadConfiguration() {
  return {
    module: "middleware",
    title: "Middleware",
    enabled: true,
    version: "0.1.14",
    defaults: {
      cors_enabled: false,
      cors_allow_origins: [
  "*"
],
      cors_allow_methods: [
  "*"
],
      cors_allow_headers: [
  "*"
],
      cors_allow_credentials: true,
      process_time_header: true,
      service_header: true,
      service_header_name: "X-Service",
      service_name: null,
      custom_headers: true,
      custom_header_name: "X-Custom-Header",
      custom_header_value: "RapidKit",
      metadata: {},
    },
  };
}

module.exports = {
  loadConfiguration,
};
