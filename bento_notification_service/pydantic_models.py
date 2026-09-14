from datetime import datetime

from pydantic import BaseModel

__all__ = [
    "NotificationResponse",
]


class NotificationResponse(BaseModel):
    id: str
    title: str
    description: str
    notification_type: str | None
    action_target: str | None
    read: bool
    timestamp: datetime
