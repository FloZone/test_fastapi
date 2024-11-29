from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

# TODO store to env var
DATABASE_URL = "postgresql://user:password@localhost:5435/database"
engine = create_engine(DATABASE_URL)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


DBSession = Annotated[Session, Depends(get_session)]
