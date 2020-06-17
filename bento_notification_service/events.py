from bento_lib.events import EventBus
from bento_lib.events.types import (
    EVENT_CREATE_NOTIFICATION,
    EVENT_NOTIFICATION,
    EVENT_NOTIFICATION_SCHEMA
)
import redis
from .app import application, db
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

        if n:
            event_bus.publish_service_event(
                application.config['SERVICE_ARTIFACT'],
                EVENT_NOTIFICATION,
                n.serialize
            )


# Not fake-able, redis is required here
try:
    event_bus = EventBus()
    event_bus.register_service_event_type(EVENT_NOTIFICATION, EVENT_NOTIFICATION_SCHEMA)

    event_bus.add_handler("bento.*", event_handler)
    event_bus.start_event_loop()
except redis.exceptions.ConnectionError:
    application.logger.error("Could not start event bus, there is an issue with Redis")
