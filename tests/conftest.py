import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture(autouse=True)
def config_env(monkeypatch):
    monkeypatch.setenv("BENTO_AUTHZ_ENABLED", "false")

    from bento_notification_service.config import get_config

    get_config.cache_clear()
    yield
    get_config.cache_clear()


@pytest.fixture()
def session_maker():
    from bento_notification_service.models import Base

    # StaticPool: every connection must share the same in-memory database
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    yield sessionmaker(engine, expire_on_commit=False)
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def client(monkeypatch, session_maker):
    from bento_notification_service import app as app_module
    from bento_notification_service.db import get_session

    # Redis isn't needed to test the HTTP API; the event handler is tested separately.
    monkeypatch.setattr(app_module, "start_event_bus", lambda *_a, **_k: None)

    application = app_module.create_app()

    def _get_test_session():
        with session_maker() as session:
            yield session

    application.dependency_overrides[get_session] = _get_test_session

    with TestClient(application) as c:
        yield c

    application.dependency_overrides.clear()


# if not in session scope we get DetachedInstanceError, not bound to a Session
@pytest.fixture()
def notification(session_maker):
    from bento_notification_service.models import Notification

    n = Notification(title="some title", description="some description")

    # Manually set ID for consistency's sake
    n.id = "da980925-244f-49ff-ab2f-b98a3a041b9a"

    with session_maker() as session:
        session.add(n)
        session.commit()

    yield n
