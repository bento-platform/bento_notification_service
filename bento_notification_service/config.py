import os

from .constants import APP_DIR, SERVICE_TYPE


__all__ = [
    "BASEDIR",
    "Config",
]


# DATABASE is set when deployed inside chord_singularity
BASEDIR = os.environ.get("DATABASE", APP_DIR.parent)


class Config:
    BENTO_DEBUG = os.environ.get("BENTO_DEBUG", "false").strip().lower() in ("1", "true")

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASEDIR, "db.sqlite3")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVICE_ID = os.environ.get("SERVICE_ID", ":".join(SERVICE_TYPE.values()))

    # Resort to Redis defaults for host/port if not set
    REDIS_HOST = os.environ.get("REDIS_HOST") or "localhost"
    REDIS_PORT = os.environ.get("REDIS_PORT") or 6379
