from contextlib import asynccontextmanager

from bento_lib.apps.fastapi import BentoFastAPI

from . import __version__
from .authz import get_authz_middleware
from .config import BENTO_EXTRA_SERVICE_INFO, get_config
from .constants import SERVICE_TYPE
from .db import get_session_maker
from .events import start_event_bus, stop_event_bus
from .logger import logger
from .routes import notification_router

__all__ = ["create_app"]


@asynccontextmanager
async def lifespan(_app: BentoFastAPI):
    # Start the event loop, or exit the service if Redis isn't available
    start_event_bus(get_config(), get_session_maker())
    try:
        yield
    finally:
        stop_event_bus()


def create_app() -> BentoFastAPI:
    # BentoFastAPI sets up CORS, authorization, Bento-formatted error handlers, and the /service-info endpoint.
    application = BentoFastAPI(
        get_authz_middleware(),
        get_config(),
        logger,
        BENTO_EXTRA_SERVICE_INFO,
        SERVICE_TYPE,
        __version__,
        lifespan=lifespan,
    )
    application.include_router(notification_router)
    return application
