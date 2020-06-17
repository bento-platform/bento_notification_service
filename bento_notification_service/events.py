import redis

from bento_lib.events import EventBus
from bento_lib.events.types import (
    EVENT_CREATE_NOTIFICATION,
    EVENT_NOTIFICATION,
    EVENT_NOTIFICATION_SCHEMA
)

from .app import application
from .db import db
from .constants import SERVICE_ARTIFACT, EVENT_PATTERN
from .models import Notification


def event_handler(message):
    event = message["data"]

    if event["type"] == EVENT_CREATE_NOTIFICATION:
        n = Notification(
            title=event["data"]["title"],
            description=event["data"]["description"],
            notification_type=event["data"]["notification_type"],
            action_target=event["data"]["action_target"]
        )

        db.session.add(n)
        db.session.commit()

        if not n:
            return

        event_bus.publish_service_event(
            SERVICE_ARTIFACT,
            EVENT_NOTIFICATION,
            n.serialize
        )


# Not fake-able, redis is required here
try:
    event_bus = EventBus()
    event_bus.register_service_event_type(EVENT_NOTIFICATION, EVENT_NOTIFICATION_SCHEMA)

    event_bus.add_handler(EVENT_PATTERN, event_handler)
    event_bus.start_event_loop()
except redis.exceptions.ConnectionError:  # pragma: no cover
    application.logger.error("Could not connect to Redis")
    exit(1)
