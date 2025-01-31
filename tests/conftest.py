from datetime import datetime, timedelta

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src import settings as main_settings
from src.database import get_session
from src.main import app
from src.modules.bookings.models import BookingInDb
from src.modules.resources.models import ResourceInDb, RoomType
from src.modules.users.models import Role, UserInDb
from src.security import get_current_user, hash_password


class TestSettings(BaseSettings):
    __test__ = False
    DATABASE_URL: str = "dummy"
    SECRET_KEY: str = "dummy"
    model_config = SettingsConfigDict()


main_settings.Settings = TestSettings


@pytest_asyncio.fixture
async def session():
    """Database session fixture with in memory database."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", connect_args={"check_same_thread": False})
    DbAsyncSession = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async with DbAsyncSession() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture
def client(session):
    """Test API client that depends on the session fixture."""

    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def client_user(session, base_user):
    """Test API client that depends on the session fixture, authenticated with 'base_user' user."""
    app.dependency_overrides[get_current_user] = lambda: base_user
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def client_admin(session, base_admin):
    """Test API client that depends on the session fixture, authenticated with 'base_admin' user."""
    app.dependency_overrides[get_current_user] = lambda: base_admin
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def base_user(session) -> UserInDb:
    user = UserInDb(name="Fixture user", email="fixture_user@test.com", password=hash_password("password"))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def base_admin(session) -> UserInDb:
    user = UserInDb(
        name="Fixture admin", email="fixture_admin@test.com", password=hash_password("password"), role=Role.ADMIN
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def resource_1(session) -> ResourceInDb:
    resource = ResourceInDb(
        name="fixture meeting room", location="france", capacity=10, room_type=RoomType.MEETING_ROOM
    )
    session.add(resource)
    await session.commit()
    await session.refresh(resource)
    return resource


@pytest_asyncio.fixture()
async def resource_2(session) -> ResourceInDb:
    resource = ResourceInDb(name="fixture auditorium", location="spain", capacity=250, room_type=RoomType.AUDITORIUM)
    session.add(resource)
    await session.commit()
    await session.refresh(resource)
    return resource


@pytest_asyncio.fixture()
async def booking_user(session, resource_1, base_user) -> BookingInDb:
    now = datetime.now().astimezone()
    start = now + timedelta(hours=1)
    end = now + timedelta(hours=2)
    booking = BookingInDb(
        title="fixture booking user 1", owner_id=base_user.id, resource_id=resource_1.id, start=start, end=end
    )
    session.add(booking)
    await session.commit()
    await session.refresh(booking)
    return booking


@pytest_asyncio.fixture()
async def booking_admin(session, resource_1, base_admin) -> BookingInDb:
    now = datetime.now().astimezone()
    start = now + timedelta(hours=4)
    end = now + timedelta(hours=5)
    booking = BookingInDb(
        title="fixture booking admin 1", owner_id=base_admin.id, resource_id=resource_1.id, start=start, end=end
    )
    session.add(booking)
    await session.commit()
    await session.refresh(booking)
    return booking
