from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from .settings import settings

DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


DBSession = Annotated[Session, Depends(get_session)]
