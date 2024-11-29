from fastapi import APIRouter, HTTPException
from sqlmodel import select

from src.database import DBSession

from .models import UserIn, UserInDb, UserOut

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
def create(user: UserIn, db: DBSession) -> UserOut:
    user_db = UserInDb.model_validate(user)
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db


@router.get("/")
def list(db: DBSession) -> list[UserOut]:
    users = db.exec(select(UserInDb))
    return users


@router.get("/{id}")
def get(id: int, db: DBSession) -> UserOut:
    user = db.get(UserInDb, id)
    if not user:
        raise HTTPException(status_code=404)
    return user


@router.delete("/{id}", status_code=204)
def delete(id: int, db: DBSession):
    user = db.get(UserInDb, id)
    if not user:
        raise HTTPException(status_code=404)
    db.delete(user)
    db.commit()
