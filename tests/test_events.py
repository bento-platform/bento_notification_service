from bento_lib.events.notifications import format_notification
from bento_lib.events.types import EVENT_CREATE_NOTIFICATION
from sqlalchemy import select

from bento_notification_service.events import _handle_event
from bento_notification_service.models import HandledCreateNotifEvent, Notification


def _message(event_id: str | None = "event-1"):
    return {
        "data": {
            "type": EVENT_CREATE_NOTIFICATION,
            **({"id": event_id} if event_id else {}),
            "data": format_notification("t", "d", "some_type", "/somewhere"),
        }
    }


async def test_create_notification_event(session_maker):
    payload = await _handle_event(session_maker, _message())

    async with session_maker() as session:
        notifications = (await session.scalars(select(Notification))).all()
        assert len(notifications) == 1
        assert notifications[0].title == "t"
        assert (await session.get(HandledCreateNotifEvent, "event-1")).notification == notifications[0].id

    assert payload is not None
    assert payload["title"] == "t"


async def test_create_notification_event_deduplicated(session_maker):
    assert await _handle_event(session_maker, _message()) is not None
    assert await _handle_event(session_maker, _message()) is None

    async with session_maker() as session:
        assert len((await session.scalars(select(Notification))).all()) == 1


async def test_other_event_types_ignored(session_maker):
    assert await _handle_event(session_maker, {"data": {"type": "something_else", "data": {}}}) is None

    async with session_maker() as session:
        assert (await session.scalars(select(Notification))).all() == []
