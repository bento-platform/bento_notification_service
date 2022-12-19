import os
from pathlib import Path

from bento_lib.types import GA4GHServiceType, GA4GHServiceOrganization
from bento_notification_service import __version__

__all__ = [
    "APP_DIR",
    "MIGRATION_DIR",
    "SERVICE_NAME",
    "SERVICE_ARTIFACT",
    "SERVICE_TYPE",
    "ORG_C3G",
    "EVENT_PATTERN",
]

APP_DIR = Path(__file__).resolve().parents[0]
MIGRATION_DIR = os.path.join(APP_DIR, "migrations")

SERVICE_NAME = "Bento Notification Service"
SERVICE_ARTIFACT = "notification"
SERVICE_TYPE: GA4GHServiceType = {
    "group": "ca.c3g.bento",
    "artifact": SERVICE_ARTIFACT,
    "version": __version__,
}

ORG_C3G: GA4GHServiceOrganization = {
    "name": "C3G",
    "url": "https://www.computationalgenomics.ca"
}

EVENT_PATTERN = "bento.*"
