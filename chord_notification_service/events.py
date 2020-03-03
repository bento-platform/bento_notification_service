from chord_lib.events import EventBus
from chord_lib.events.types import EVENT_NOTIFICATION, EVENT_NOTIFICATION_SCHEMA
from .app import db
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
event_bus = EventBus()
event_bus.register_service_event_type(EVENT_NOTIFICATION, EVENT_NOTIFICATION_SCHEMA)

event_bus.add_handler("chord.*", event_handler)
event_bus.start_event_loop()
