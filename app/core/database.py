from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import get_settings

engine = create_async_engine(get_settings().DATABASE_URL)

DbAsyncSession = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_session():
    async with DbAsyncSession() as session:
        yield session


DBSession = Annotated[AsyncSession, Depends(get_session)]
