import os

from bento_lib.service_info.types import GA4GHServiceType, GA4GHServiceOrganization
from pathlib import Path

from . import __version__

__all__ = [
    "APP_DIR",
    "MIGRATION_DIR",
    "BENTO_SERVICE_KIND",
    "SERVICE_NAME",
    "SERVICE_ARTIFACT",
    "SERVICE_TYPE",
    "ORG_C3G",
    "EVENT_PATTERN",
]

APP_DIR = Path(__file__).resolve().parents[0]
MIGRATION_DIR = os.path.join(APP_DIR, "migrations")

BENTO_SERVICE_KIND = "notification"
SERVICE_NAME = "Bento Notification Service"
SERVICE_ARTIFACT = BENTO_SERVICE_KIND
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
