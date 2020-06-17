import os
from pathlib import Path

from bento_notification_service import __version__

__all__ = [
    "APP_DIR",
    "MIGRATION_DIR",
    "SERVICE_NAME",
    "SERVICE_ARTIFACT",
    "SERVICE_TYPE",
    "EVENT_PATTERN",
]

APP_DIR = Path(__file__).resolve().parents[0]
MIGRATION_DIR = os.path.join(APP_DIR, "migrations")

SERVICE_NAME = "Bento Notification Service"
SERVICE_ARTIFACT = "notification"
SERVICE_TYPE = f"ca.c3g.bento:{SERVICE_ARTIFACT}:{__version__}"

EVENT_PATTERN = "bento.*"
