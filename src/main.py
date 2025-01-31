from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from .database import DBSession
from .modules.bookings import router as bookings
from .modules.resources import router as resources
from .modules.users import router as users
from .modules.users.models import UserOut
from .security import AuthenticatedUser, Token, authenticate_user, generate_access_token

# Remove auto-generated 422 errors from redoc and swagger docs
_openapi = FastAPI.openapi


def openapi(self: FastAPI):
    _openapi(self)
    for _, method_item in self.openapi_schema.get("paths").items():
        for _, param in method_item.items():
            responses = param.get("responses")
            # Remove 422 response
            if "422" in responses:
                del responses["422"]
    return self.openapi_schema


FastAPI.openapi = openapi


app = FastAPI()
app.include_router(bookings.router)
app.include_router(resources.router)
app.include_router(users.router)


# All int validation errors now return 400 error instead of 422
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors()},
    )


@app.get("/")
async def hello_world():
    """Hello World!"""
    return {"Hello": "World!"}


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DBSession) -> Token:
    """Login user with his email and password and return access_token to access the API."""
    user = await authenticate_user(form_data.username, form_data.password, db)

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
    """Get current user data."""
    return current_user
