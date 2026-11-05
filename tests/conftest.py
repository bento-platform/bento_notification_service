import pytest
import pytest_asyncio
from httpx2 import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool


@pytest.fixture(autouse=True)
def config_env(monkeypatch):
    monkeypatch.setenv("BENTO_AUTHZ_ENABLED", "false")

    from bento_notification_service.config import get_config

    get_config.cache_clear()
    yield
    get_config.cache_clear()


@pytest_asyncio.fixture()
async def session_maker():
    from bento_notification_service.models import Base

    # StaticPool: every connection must share the same in-memory database
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()


@pytest_asyncio.fixture()
async def client(monkeypatch, session_maker):
    from bento_notification_service import app as app_module
    from bento_notification_service.db import get_session

    # Redis isn't needed to test the HTTP API; the event handler is tested separately.
    monkeypatch.setattr(app_module, "start_event_bus", lambda *_a, **_k: None)

    application = app_module.create_app()

    async def _get_test_session():
        async with session_maker() as session:
            yield session

    application.dependency_overrides[get_session] = _get_test_session

    async with AsyncClient(transport=ASGITransport(app=application), base_url="http://test") as c:
        yield c

    application.dependency_overrides.clear()


# if not in session scope we get DetachedInstanceError, not bound to a Session
@pytest_asyncio.fixture()
async def notification(session_maker):
    from bento_notification_service.models import Notification

    n = Notification(title="some title", description="some description")

    # Manually set ID for consistency's sake
    n.id = "da980925-244f-49ff-ab2f-b98a3a041b9a"

    async with session_maker() as session:
        session.add(n)
        await session.commit()

    yield n
