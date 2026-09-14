from datetime import timezone
from uuid import uuid4

from sqlalchemy.sql import func

from .db import db
from .pydantic_models import NotificationResponse

__all__ = [
    "Notification",
    "HandledCreateNotifEvent",
]


class Notification(db.Model):
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    notification_type = db.Column(db.String)
    action_target = db.Column(db.String)
    _read = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, server_default=func.now())

    def __init__(self, *args, **kwargs):
        self.id = str(uuid4())
        super().__init__(*args, **kwargs)

    @property
    def read(self):
        return bool(self._read)

    def is_read(self):
        self._read = 1

    def serialize(self):
        """
        Serializes a notification database object as a JSON-compatible dictionary via Pydantic.
        TODO: future: just return Pydantic instance for FastAPI port
        """
        return NotificationResponse(
            id=self.id,
            title=self.title,
            description=self.description,
            notification_type=self.notification_type,
            action_target=self.action_target,
            read=bool(self.read),
            timestamp=self.timestamp.astimezone(timezone.utc),
        ).model_dump(mode="json")


class HandledCreateNotifEvent(db.Model):
    """
    Representation of a handled create_notification event, to allow for scaling the notification service
    without accidentally handling an event more than once.
    """

    id = db.Column(db.String, primary_key=True)
    notification = db.Column(db.String, db.ForeignKey(f"{Notification.__table__}.id"), nullable=False)
    handled_at = db.Column(db.DateTime, server_default=func.now())
