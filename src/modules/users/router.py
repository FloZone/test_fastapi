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
async def create(user: UserIn, db: DBSession) -> UserOut:
    """Create an user."""
    user_db = UserInDb.model_validate(user)
    user_db.set_password(user_db.password)
    db.add(user_db)
    try:
        await db.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    await db.refresh(user_db)
    return user_db


@router.get("/")
async def list(db: DBSession, current_user: AuthenticatedUser, offset: int = 0, limit: int = 100) -> list[UserOut]:
    """List all users."""
    users = (await db.execute(select(UserInDb).offset(offset).limit(limit))).scalars().all()
    return users


@router.get("/{id}", responses={404: {"description": "Not found"}})
async def get(id: int, db: DBSession, current_user: AuthenticatedUser) -> UserOut:
    """Get an user data."""
    user = await db.get(UserInDb, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user


@router.delete("/{id}", status_code=204, responses={404: {"description": "Not found"}})
async def delete(id: int, db: DBSession, current_user: AuthenticatedUser, _: bool = Depends(AllowRole([Role.ADMIN]))):
    """[Admin] Delete an user."""
    user = await db.get(UserInDb, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await db.delete(user)
    await db.commit()
