import configparser
import os
from pathlib import Path


config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), "package.cfg"))


VERSION = config["package"]["version"]
APP_DIR = Path(__file__).resolve().parents[0]

if "DATABASE" in os.environ:
    # when deployed inside chord_singularity
    BASEDIR = os.environ["DATABASE"]
else:
    BASEDIR = APP_DIR.parent


class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, "db.sqlite3")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    VERSION = VERSION
    SERVICE_ARTIFACT = "notification"
    SERVICE_TYPE = "ca.c3g.chord:notification:{}".format(VERSION)
    SERVICE_ID = os.environ.get("SERVICE_ID", SERVICE_TYPE)
    SERVICE_NAME = "CHORD Notification Service"
