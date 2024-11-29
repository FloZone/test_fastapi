from fastapi import APIRouter, HTTPException
from sqlmodel import select

from src.database import DBSession

from .models import UserIn, UserInDb, UserOut

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/")
def create(user: UserIn, db: DBSession) -> UserOut:
    """Create an user."""
    user_db = UserInDb.model_validate(user)
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db


@router.get("/")
def list(db: DBSession) -> list[UserOut]:
    """List all users."""
    users = db.exec(select(UserInDb))
    return users


@router.get(
    "/{id}",
    responses={404: {"description": "Not found"}},
)
def get(id: int, db: DBSession) -> UserOut:
    """Get user data."""
    user = db.get(UserInDb, id)
    if not user:
        raise HTTPException(status_code=404)
    return user


@router.delete(
    "/{id}",
    status_code=204,
    responses={404: {"description": "Not found"}},
)
def delete(id: int, db: DBSession):
    """Delete an user."""
    user = db.get(UserInDb, id)
    if not user:
        raise HTTPException(status_code=404)
    db.delete(user)
    db.commit()
