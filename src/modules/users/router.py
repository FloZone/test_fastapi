from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from ...database import DBSession
from ...security import AllowRole, AuthenticatedUser
from .models import Role, UserIn, UserInDb, UserOut

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/", responses={400: {"description": "User already exists"}})
def create(user: UserIn, db: DBSession) -> UserOut:
    """Create an user."""
    user_db = UserInDb.model_validate(user)
    user_db.set_password(user_db.password)
    db.add(user_db)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    db.refresh(user_db)
    return user_db


@router.get("/")
def list(db: DBSession, current_user: AuthenticatedUser) -> list[UserOut]:
    """List all users."""
    users = db.exec(select(UserInDb))
    return users


@router.get("/{id}", responses={404: {"description": "Not found"}})
def get(id: int, db: DBSession, current_user: AuthenticatedUser) -> UserOut:
    """Get an user data."""
    user = db.get(UserInDb, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user


@router.delete("/{id}", status_code=204, responses={404: {"description": "Not found"}})
def delete(id: int, db: DBSession, current_user: AuthenticatedUser, _: bool = Depends(AllowRole([Role.ADMIN]))):
    """[Admin] Delete an user."""
    user = db.get(UserInDb, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.delete(user)
    db.commit()
