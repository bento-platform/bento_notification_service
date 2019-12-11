import os
import sqlite3
import uuid

from datetime import datetime, timezone
from flask import current_app, g
from typing import Optional

from .notifications import notification_dict

__all__ = [
    "DATABASE",
    "get_new_db_connection",
    "get_db",
    "close_db",
    "init_db",
    "update_db",
    "get_notification",
    "create_notification",
]


DATABASE = os.environ.get("DATABASE", "chord_notification_service.db")


def get_new_db_connection():
    return sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)


def get_db():
    if "db" not in g:
        g.db = get_new_db_connection()
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(_e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as sf:
        db.executescript(sf.read().decode("utf-8"))

    db.commit()


def update_db():
    db = get_db()
    c = db.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications'")
    if c.fetchone() is None:
        init_db()
        return

    # TODO


def get_notification(c, n_id: str) -> Optional[dict]:
    c.execute("SELECT * FROM notifications WHERE id = ?", (n_id,))
    n = c.fetchone()
    if n is None:
        return None

    return notification_dict(n)


def create_notification(db, c, title, description, notification_type, action_target) -> Optional[str]:
    new_id = str(uuid.uuid4())  # TODO: Prevent conflict
    c.execute("SELECT * FROM notifications WHERE id = ?", (new_id,))
    if c.fetchone() is not None:
        return None

    c.execute("INSERT INTO notifications (id, title, description, notification_type, action_target, timestamp) "
              "VALUES (?, ?, ?, ?, ?, ?)",
              (new_id, title, description, notification_type, action_target, datetime.now(timezone.utc).isoformat()))
    db.commit()
    return new_id
