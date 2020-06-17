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
