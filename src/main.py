from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from .database import DBSession
from .modules.users import router as users
from .modules.users.models import UserOut
from .security import AuthenticatedUser, Token, authenticate_user, generate_access_token

app = FastAPI()
app.include_router(users.router)


@app.get("/")
async def hello_world():
    return {"Hello": "World!"}


@app.post("/token")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DBSession) -> Token:
    """Login user with his email and password and return access_token to access the API."""
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Generate the access token
    access_token = generate_access_token(data={"sub": user.email, "name": user.name})
    return Token(access_token=access_token, token_type="bearer")


@app.get("/me")
def me(current_user: AuthenticatedUser) -> UserOut:
    return current_user
