from flask_sqlalchemy import SQLAlchemy

from .models import Base

__all__ = ["db"]

db: SQLAlchemy = SQLAlchemy(model_class=Base)
