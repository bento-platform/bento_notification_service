import os

from bento_lib.service_info.helpers import build_bento_service_type
from bento_lib.service_info.types import GA4GHServiceType
from pathlib import Path

from . import __version__

__all__ = [
    "APP_DIR",
    "MIGRATION_DIR",
    "BENTO_SERVICE_KIND",
    "SERVICE_NAME",
    "SERVICE_ARTIFACT",
    "SERVICE_TYPE",
    "EVENT_PATTERN",
]

APP_DIR = Path(__file__).resolve().parents[0]
MIGRATION_DIR = os.path.join(APP_DIR, "migrations")

BENTO_SERVICE_KIND = "notification"
SERVICE_NAME = "Bento Notification Service"
SERVICE_ARTIFACT = BENTO_SERVICE_KIND
SERVICE_TYPE: GA4GHServiceType = build_bento_service_type(SERVICE_ARTIFACT, __version__)

EVENT_PATTERN = "bento.*"
