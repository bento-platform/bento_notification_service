import asyncio
import sys
from collections.abc import Callable

import redis
from bento_lib.events import EventBus
from bento_lib.events.types import EVENT_CREATE_NOTIFICATION, EVENT_NOTIFICATION, EVENT_NOTIFICATION_SCHEMA
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .config import Config
from .constants import EVENT_PATTERN, SERVICE_ARTIFACT
from .logger import logger
from .models import HandledCreateNotifEvent, Notification

__all__ = ["start_event_bus", "stop_event_bus"]


# Global event bus tracker
_global_event_bus: EventBus | None = None


async def _handle_event(session_maker: async_sessionmaker[AsyncSession], message: dict) -> dict | None:
    """
    Handles a create-notification event, returning the JSON payload of the notification event to publish, or None if
    nothing was created.
    """

    event = message["data"]

    if event["type"] != EVENT_CREATE_NOTIFICATION:
        return None

    logger.debug(f"Received message: {message} (event: {event})")

    event_id = event.get("id")

    async with session_maker() as session:
        if event_id and await session.get(HandledCreateNotifEvent, event_id):
            logger.warning(f"Already handled event: {event_id}")
            return None

        n = Notification(
            title=event["data"]["title"],
            description=event["data"]["description"],
            notification_type=event["data"]["notification_type"],
            action_target=event["data"]["action_target"],
        )
        session.add(n)

        # Events only have IDs if the event creator is using bento_lib >= 5.3
        if event_id:
            # Don't commit until we actually create the notification
            session.add(HandledCreateNotifEvent(id=event_id, notification=n.id))

        await session.commit()
        return n.to_pydantic().model_dump(mode="json")


def _make_event_handler(
    eb: EventBus, session_maker: async_sessionmaker[AsyncSession], loop: asyncio.AbstractEventLoop
) -> Callable[[dict], None]:
    # The event bus calls handlers from its own (synchronous) thread, but the async engine is bound to the application's
    # event loop - so we run the database work on that loop and block this thread until it's done.
    def _event_handler(message: dict) -> None:
        payload = asyncio.run_coroutine_threadsafe(_handle_event(session_maker, message), loop).result()
        if payload is not None:
            eb.publish_service_event(SERVICE_ARTIFACT, EVENT_NOTIFICATION, payload)

    return _event_handler


def start_event_bus(
    config: Config, session_maker: async_sessionmaker[AsyncSession], loop: asyncio.AbstractEventLoop
) -> None:
    global _global_event_bus

    if _global_event_bus:  # Don't double-instantiate the event bus, but do make sure it's running
        _global_event_bus.start_event_loop()
        return

    # Not fake-able, redis is required here
    try:
        _global_event_bus = event_bus = EventBus(host=config.redis_host, port=config.redis_port, logger=logger)
        event_bus.register_service_event_type(EVENT_NOTIFICATION, EVENT_NOTIFICATION_SCHEMA)

        event_bus.add_handler(EVENT_PATTERN, _make_event_handler(event_bus, session_maker, loop))
        event_bus.start_event_loop()
    except redis.exceptions.ConnectionError:  # pragma: no cover
        logger.error("Could not connect to Redis")
        sys.exit(1)


def stop_event_bus() -> None:
    global _global_event_bus
    if _global_event_bus:
        _global_event_bus.stop_event_loop()
        _global_event_bus = None
