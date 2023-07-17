import logging
import os

from .constants import APP_DIR, SERVICE_TYPE
from .logger import logger as logger_

__all__ = [
    "BASEDIR",
    "Config",
]


TRUTH_VALUES = ("true", "1")

# DATABASE is set when deployed inside chord_singularity
BASEDIR = os.environ.get("DATABASE", APP_DIR.parent)


def _get_from_environ_or_fail(var: str, logger: logging.Logger = logger_) -> str:
    if (val := os.environ.get(var, "")) == "":
        logger.critical(f"{var} must be set")
        exit(1)
    return val


class Config:
    BENTO_DEBUG = os.environ.get("BENTO_DEBUG", "false").strip().lower() in TRUTH_VALUES

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASEDIR, "db.sqlite3")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVICE_ID = os.environ.get("SERVICE_ID", ":".join(SERVICE_TYPE.values()))

    # Resort to Redis defaults for host/port if not set
    REDIS_HOST = os.environ.get("REDIS_HOST") or "localhost"
    REDIS_PORT = os.environ.get("REDIS_PORT") or 6379

    # Authz
    AUTHZ_ENABLED = os.environ.get("AUTHZ_ENABLED", "true").strip().lower() in TRUTH_VALUES
    AUTHZ_URL: str = _get_from_environ_or_fail("BENTO_AUTHZ_SERVICE_URL").strip().rstrip("/") if AUTHZ_ENABLED else ""
