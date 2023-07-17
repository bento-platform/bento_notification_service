from bento_lib.auth.middleware.flask import FlaskAuthMiddleware
from .config import Config

__all__ = [
    "authz_middleware",
    "PERMISSION_VIEW_NOTIFICATIONS",
]

authz_middleware = FlaskAuthMiddleware(
    Config.AUTHZ_URL,
    debug_mode=Config.BENTO_DEBUG,
    enabled=Config.AUTHZ_ENABLED,
)

PERMISSION_VIEW_NOTIFICATIONS = "view:notifications"