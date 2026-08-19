from flask_sqlalchemy import SQLAlchemy

__all__ = ["db"]

db: SQLAlchemy = SQLAlchemy(engine_options={"future": True})
