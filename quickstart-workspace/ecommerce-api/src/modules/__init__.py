"""Module bootstrap namespace."""

from src.modules.free.essentials.settings import (
    BaseSettings,
    CustomConfigSource,
    Field,
    Settings,
    configure_fastapi_app,
    get_settings,
    settings,
    settings_dependency,
)
import src.modules.free.essentials.logging
import src.modules.free.essentials.deployment
import src.modules.free.essentials.middleware
import src.modules.free.database.db_postgres
import src.modules.free.auth.core
from src.modules.free.cache.redis import (
    AsyncRedis,
    DEFAULTS,
    RedisClient,
    RedisSyncClient,
    SyncRedis,
    build_redis_url,
    check_redis_connection,
    describe_cache,
    get_redis,
    get_redis_metadata,
    get_redis_sync,
    list_features,
    redis_dependency,
    refresh_vendor_module,
    register_redis,
)
import src.modules.free.security.security_headers
# <<<inject:module-init>>>