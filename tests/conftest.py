from datetime import datetime, timedelta

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.core import settings as main_settings
from app.core.database import get_session
from app.core.security import get_current_user, hash_password
from app.main import app
from app.models.booking_model import BookingInDb
from app.models.resource_model import ResourceInDb, RoomType
from app.models.user_model import Role, UserInDb


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
    async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async with async_session() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture
def client(session):
    """Fixture test API client, not authenticated."""
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def client_user(session, base_user):
    """Fixture test API client, authenticated with 'base_user' user."""
    app.dependency_overrides[get_current_user] = lambda: base_user
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def client_admin(session, base_admin):
    """Fixture test API client, authenticated with 'base_admin' user."""
    app.dependency_overrides[get_current_user] = lambda: base_admin
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def base_user(session) -> UserInDb:
    """Fixture user with USER role."""
    user = UserInDb(
        name="Fixture user", email="fixture_user@test.com", password=hash_password("password"), role=Role.USER
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def base_admin(session) -> UserInDb:
    """Fixture user with ADMIN role."""
    user = UserInDb(
        name="Fixture admin", email="fixture_admin@test.com", password=hash_password("password"), role=Role.ADMIN
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def resource_1(session) -> ResourceInDb:
    """Fixture resource."""
    resource = ResourceInDb(
        name="fixture meeting room", location="france", capacity=10, room_type=RoomType.MEETING_ROOM
    )
    session.add(resource)
    await session.commit()
    await session.refresh(resource)
    return resource


@pytest_asyncio.fixture()
async def resource_2(session) -> ResourceInDb:
    """Fixture resource."""
    resource = ResourceInDb(name="fixture auditorium", location="spain", capacity=250, room_type=RoomType.AUDITORIUM)
    session.add(resource)
    await session.commit()
    await session.refresh(resource)
    return resource


@pytest_asyncio.fixture()
async def booking_user(session, resource_1, base_user) -> BookingInDb:
    """Fixture booking from USER user."""
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
    """Fixture booking from ADMIN user."""
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
