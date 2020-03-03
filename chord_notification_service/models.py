from uuid import uuid4
from datetime import timezone
from sqlalchemy.sql import func
from chord_notification_service.app import db


class Notification(db.Model):
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    notification_type = db.Column(db.String)
    action_target = db.Column(db.String)
    read = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, server_default=func.now())

    def __init__(self, *args, **kwargs):
        self.id = str(uuid4())
        super().__init__(*args, **kwargs)

    def is_read(self):
        self.read = 1

    @property
    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "notification_type": self.notification_type,
            "action_target": self.action_target,
            "read": bool(self.read),
            "timestamp": self.timestamp.astimezone(timezone.utc).isoformat()
        }
