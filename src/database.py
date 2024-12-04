from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine

from .settings import get_settings


def get_session():
    with Session(create_engine(get_settings().DATABASE_URL)) as session:
        yield session


DBSession = Annotated[Session, Depends(get_session)]
