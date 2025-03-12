import redis

from flask import Flask

from bento_lib.events import EventBus
from bento_lib.events.types import EVENT_CREATE_NOTIFICATION, EVENT_NOTIFICATION, EVENT_NOTIFICATION_SCHEMA

from .db import db
from .constants import SERVICE_ARTIFACT, EVENT_PATTERN
from .models import Notification, HandledCreateNotifEvent


__all__ = ["start_event_bus"]


# Global event bus tracker
_global_event_bus: EventBus | None = None


def start_event_bus(application: Flask):
    global _global_event_bus

    if _global_event_bus:  # Don't double-instantiate the event bus, but do make sure it's running
        _global_event_bus.start_event_loop()
        return

    def event_handler(eb: EventBus):
        def _event_handler(message):
            event = message["data"]

            # print(f"got event {event} for event bus {repr(eb)}")

            if event["type"] != EVENT_CREATE_NOTIFICATION:
                return

            with application.app_context():
                application.logger.debug(f"Recieved message: {message} (event: {event})")

                event_id = event.get("id")

                if event_id and HandledCreateNotifEvent.query.filter_by(id=event_id).first():
                    application.logger.warning(f"Already handled event: {event_id}")
                    return

                n = Notification(
                    title=event["data"]["title"],
                    description=event["data"]["description"],
                    notification_type=event["data"]["notification_type"],
                    action_target=event["data"]["action_target"],
                )

                db.session.add(n)

                # Events only have IDs if the event creator is using bento_lib >= 5.3
                if event_id := event.get("id"):
                    he = HandledCreateNotifEvent(id=event_id, notification=n.id)
                    db.session.add(he)  # Don't commit until we actually create the notification

                db.session.commit()

                if not n:
                    return

                eb.publish_service_event(SERVICE_ARTIFACT, EVENT_NOTIFICATION, n.serialize)

        return _event_handler

    redis_config = {
        "host": application.config["REDIS_HOST"],
        "port": application.config["REDIS_PORT"],
    }

    # Not fake-able, redis is required here
    try:
        _global_event_bus = event_bus = EventBus(**redis_config)
        event_bus.register_service_event_type(EVENT_NOTIFICATION, EVENT_NOTIFICATION_SCHEMA)

        event_bus.add_handler(EVENT_PATTERN, event_handler(event_bus))
        event_bus.start_event_loop()
    except redis.exceptions.ConnectionError:  # pragma: no cover
        application.logger.error("Could not connect to Redis")
        exit(1)
