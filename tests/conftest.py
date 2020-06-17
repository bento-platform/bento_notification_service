import os
import pytest
from bento_notification_service.app import application, db
from bento_notification_service.config import BASEDIR
from bento_notification_service.models import Notification


SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, "test.sqlite3")


@pytest.fixture(scope='session')
def client():
    application.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    db.create_all()

    yield application.test_client()

    db.session.remove()
    db.drop_all()


# if not in session scope we get DetachedInstanceError, not bound to a Session
@pytest.fixture(scope='session')
def notification():
    n = Notification(
        title='some title',
        description='some description'
    )

    db.session.add(n)
    db.session.commit()

    yield n
