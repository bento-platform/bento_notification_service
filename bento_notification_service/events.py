import sys
from collections.abc import Callable

import redis
from bento_lib.events import EventBus
from bento_lib.events.types import EVENT_CREATE_NOTIFICATION, EVENT_NOTIFICATION, EVENT_NOTIFICATION_SCHEMA
from sqlalchemy.orm import Session, sessionmaker

from .config import Config
from .constants import EVENT_PATTERN, SERVICE_ARTIFACT
from .logger import logger
from .models import HandledCreateNotifEvent, Notification

__all__ = ["start_event_bus", "stop_event_bus"]


# Global event bus tracker
_global_event_bus: EventBus | None = None


def _make_event_handler(eb: EventBus, session_maker: sessionmaker[Session]) -> Callable[[dict], None]:
    def _event_handler(message: dict) -> None:
        event = message["data"]

        if event["type"] != EVENT_CREATE_NOTIFICATION:
            return

        logger.debug(f"Received message: {message} (event: {event})")

        event_id = event.get("id")

        with session_maker() as session:
            if event_id and session.get(HandledCreateNotifEvent, event_id):
                logger.warning(f"Already handled event: {event_id}")
                return

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

            session.commit()
            payload = n.to_pydantic().model_dump(mode="json")

        eb.publish_service_event(SERVICE_ARTIFACT, EVENT_NOTIFICATION, payload)

    return _event_handler


def start_event_bus(config: Config, session_maker: sessionmaker[Session]) -> None:
    global _global_event_bus

    if _global_event_bus:  # Don't double-instantiate the event bus, but do make sure it's running
        _global_event_bus.start_event_loop()
        return

    # Not fake-able, redis is required here
    try:
        _global_event_bus = event_bus = EventBus(host=config.redis_host, port=config.redis_port, logger=logger)
        event_bus.register_service_event_type(EVENT_NOTIFICATION, EVENT_NOTIFICATION_SCHEMA)

        event_bus.add_handler(EVENT_PATTERN, _make_event_handler(event_bus, session_maker))
        event_bus.start_event_loop()
    except redis.exceptions.ConnectionError:  # pragma: no cover
        logger.error("Could not connect to Redis")
        sys.exit(1)


def stop_event_bus() -> None:
    global _global_event_bus
    if _global_event_bus:
        _global_event_bus.stop_event_loop()
        _global_event_bus = None
