from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import select

from app.core.database import DBSession
from app.core.exceptions import NotFoundException
from app.core.settings import get_settings
from app.models.user_model import Role, UserInDb
from app.services.user_service import UserService

# Authent method: login + password -> JWT access token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=get_settings().API_PATH + "/token")
# Password hash method
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Access token generation method
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str


def hash_password(password: str) -> str:
    """Return a hashed password from the given password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return whether the given clear password is the same as the hashed one."""
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(username: str, password: str, user_service: UserService) -> UserInDb:
    """
    Validate the given username (used as email) and password and return the corresponding user, of False if creds are
    not matching.
    """
    try:
        user = await user_service.get_with_username(username)
    except NotFoundException:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def generate_access_token(data: dict):
    """Generate a JWT access token from given user data."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, get_settings().SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DBSession):
    """Get current authenticated user from JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Validate the access token
    try:
        payload = jwt.decode(token, get_settings().SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    # Get the corresponding user
    user = (await db.execute(select(UserInDb).where(UserInDb.email == username))).scalars().first()
    if not user:
        raise credentials_exception
    return user


class AllowRole:
    """Helper to check if currently connected user has the given rights."""

    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: Annotated[UserInDb, Depends(get_current_user)]):
        for role in self.allowed_roles:
            if user.role.value >= role.value:
                return True
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


# Helper for getting current authenticated user in endpoints
AuthenticatedUser = Annotated[UserInDb, Depends(get_current_user)]
