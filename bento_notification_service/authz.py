from functools import lru_cache
from typing import Annotated

from bento_lib.auth.middleware.fastapi import FastApiAuthMiddleware
from bento_lib.auth.permissions import P_VIEW_NOTIFICATIONS
from bento_lib.auth.resources import RESOURCE_EVERYTHING
from fastapi import Depends, Request

from .config import get_config
from .logger import logger

__all__ = [
    "get_authz_middleware",
    "AuthzMiddlewareDep",
    "require_view_notifications",
]

PERMISSION_SET_VIEW = frozenset({P_VIEW_NOTIFICATIONS})


@lru_cache
def get_authz_middleware() -> FastApiAuthMiddleware:
    return FastApiAuthMiddleware.build_from_fastapi_pydantic_config(get_config(), logger)


AuthzMiddlewareDep = Annotated[FastApiAuthMiddleware, Depends(get_authz_middleware)]


async def require_view_notifications(request: Request, authz: AuthzMiddlewareDep) -> None:
    """
    Router-level dependency: requires the view:notifications permission on the whole node.
    """
    if not authz.enabled:
        return
    await authz.async_check_authz_evaluate(request, PERMISSION_SET_VIEW, RESOURCE_EVERYTHING, set_authz_flag=True)
