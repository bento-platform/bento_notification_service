from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, declarative_base, mapped_column
from sqlalchemy.sql import func

from .pydantic_models import NotificationResponse

__all__ = [
    "Base",
    "Notification",
    "HandledCreateNotifEvent",
]

Base = declarative_base()


class Notification(Base):
    __tablename__ = "notification"

    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    notification_type: Mapped[str | None]
    action_target: Mapped[str | None]
    _read: Mapped[int] = mapped_column(nullable=False, default=0)
    timestamp: Mapped[datetime | None] = mapped_column(nullable=False, server_default=func.now())

    def __init__(self, *args, **kwargs):
        self.id = str(uuid4())
        super().__init__(*args, **kwargs)

    @property
    def read(self):
        return bool(self._read)

    def is_read(self):
        self._read = 1

    def to_pydantic(self):
        """
        Transforms a notification database object into a Pydantic object.
        """
        return NotificationResponse(
            id=self.id,
            title=self.title,
            description=self.description,
            notification_type=self.notification_type,
            action_target=self.action_target,
            read=bool(self.read),
            timestamp=self.timestamp.astimezone(timezone.utc),
        )


class HandledCreateNotifEvent(Base):
    """
    Representation of a handled create_notification event, to allow for scaling the notification service
    without accidentally handling an event more than once.
    """

    __tablename__ = "handled_create_notif_event"

    id: Mapped[str] = mapped_column(primary_key=True)
    notification: Mapped[str] = mapped_column(ForeignKey("notification.id"), nullable=False)
    handled_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
