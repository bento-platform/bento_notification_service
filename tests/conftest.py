import pytest
from bento_notification_service.app import application
from bento_notification_service.db import db
from bento_notification_service.models import Notification


SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def client():
    application.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI

    with application.app_context():
        db.create_all()

        yield application.test_client()

        db.session.remove()
        db.drop_all()


# if not in session scope we get DetachedInstanceError, not bound to a Session
@pytest.fixture(scope="session")
def notification():
    n = Notification(
        title="some title",
        description="some description"
    )

    # Manually set ID for consistency's sake
    n.id = "da980925-244f-49ff-ab2f-b98a3a041b9a"

    db.session.add(n)
    db.session.commit()

    yield n
