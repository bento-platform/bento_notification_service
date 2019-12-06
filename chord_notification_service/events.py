from chord_lib.events import EventBus
from chord_lib.events.types import EVENT_NOTIFICATION, EVENT_NOTIFICATION_SCHEMA


__all__ = [
    "event_bus",
]

# Not fake-able, redis is required here
event_bus = EventBus()
event_bus.register_service_event_type(EVENT_NOTIFICATION, EVENT_NOTIFICATION_SCHEMA)
