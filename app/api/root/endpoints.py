from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import AuthenticatedUser, Token, authenticate_user, generate_access_token
from app.schema.user_schema import UserWithId
from app.services.user_service import UserService

router = APIRouter()


@router.get("/")
def hello_world():
    """Hello World!"""
    return {"Hello": "World!"}


@router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], user_service: UserService = Depends()
) -> Token:
    """Login user with his email and password and return access_token to access the API."""
    user = await authenticate_user(form_data.username, form_data.password, user_service)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Generate the access token
    access_token = generate_access_token(data={"sub": user.email, "name": user.name})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me")
def me(current_user: AuthenticatedUser) -> UserWithId:
    """Get current user data."""
    return current_user
