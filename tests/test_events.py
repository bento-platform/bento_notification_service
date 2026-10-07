from bento_lib.events.notifications import format_notification
from bento_lib.events.types import EVENT_CREATE_NOTIFICATION, EVENT_NOTIFICATION
from sqlalchemy import select

from bento_notification_service.events import _make_event_handler
from bento_notification_service.models import HandledCreateNotifEvent, Notification


class FakeEventBus:
    def __init__(self):
        self.published = []

    def publish_service_event(self, service_artifact, event_type, event_data):
        self.published.append((service_artifact, event_type, event_data))


def _message(event_id: str | None = "event-1"):
    return {
        "data": {
            "type": EVENT_CREATE_NOTIFICATION,
            **({"id": event_id} if event_id else {}),
            "data": format_notification("t", "d", "some_type", "/somewhere"),
        }
    }


def test_create_notification_event(session_maker):
    bus = FakeEventBus()
    handler = _make_event_handler(bus, session_maker)

    handler(_message())

    with session_maker() as session:
        notifications = session.scalars(select(Notification)).all()
        assert len(notifications) == 1
        assert notifications[0].title == "t"
        assert session.get(HandledCreateNotifEvent, "event-1").notification == notifications[0].id

    assert len(bus.published) == 1
    assert bus.published[0][1] == EVENT_NOTIFICATION
    assert bus.published[0][2]["title"] == "t"


def test_create_notification_event_deduplicated(session_maker):
    bus = FakeEventBus()
    handler = _make_event_handler(bus, session_maker)

    handler(_message())
    handler(_message())

    with session_maker() as session:
        assert len(session.scalars(select(Notification)).all()) == 1
    assert len(bus.published) == 1


def test_other_event_types_ignored(session_maker):
    bus = FakeEventBus()
    handler = _make_event_handler(bus, session_maker)

    handler({"data": {"type": "something_else", "data": {}}})

    with session_maker() as session:
        assert session.scalars(select(Notification)).all() == []
    assert bus.published == []
