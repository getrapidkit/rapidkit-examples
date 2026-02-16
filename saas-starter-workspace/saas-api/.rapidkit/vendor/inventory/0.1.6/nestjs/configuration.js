"use strict";

const defaults = {
  "allow_backorders": false,
  "allow_negative_inventory": false,
  "decimal_precision": 2,
  "default_currency": "usd",
  "enabled": true,
  "log_level": "INFO",
  "low_stock_threshold": 5,
  "metadata": {
    "module": "inventory"
  },
  "reservation_expiry_minutes": 30
};
const pricing = {
  "max_price": 250000,
  "min_price": 0.01,
  "rounding_mode": "half_up",
  "tax_inclusive": false
};
const warehouses = {
  "primary": {
    "allow_backorders": false,
    "code": "primary",
    "location": "global",
    "name": "Primary Warehouse"
  }
};
const notifications = {
  "channels": [
    "email",
    "webhook"
  ],
  "enabled": true,
  "low_stock": {
    "include_reservations": true,
    "threshold": 3
  }
};

function loadConfiguration() {
  return {
    module: "inventory",
    title: "Inventory",
    defaults,
    pricing,
    warehouses,
    notifications,
  };
}

module.exports = {
  loadConfiguration,
};
