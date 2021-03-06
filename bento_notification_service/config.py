import os

from .constants import APP_DIR, SERVICE_TYPE


__all__ = [
    "BASEDIR",
    "Config",
]


# DATABASE is set when deployed inside chord_singularity
BASEDIR = os.environ.get("DATABASE", APP_DIR.parent)


class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASEDIR, "db.sqlite3")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVICE_ID = os.environ.get("SERVICE_ID", SERVICE_TYPE)

    # Resort to Redis defaults for host/port if not set
    REDIS_SOCKET = os.environ.get("REDIS_SOCKET")
    REDIS_HOST = os.environ.get("REDIS_HOST") or "localhost"
    REDIS_PORT = os.environ.get("REDIS_PORT") or 6379
