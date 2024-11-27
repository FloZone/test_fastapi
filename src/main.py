from fastapi import FastAPI, HTTPException
from sqlmodel import select

from src.database import DBSession
from src.models import User, UserCreate

app = FastAPI()


@app.get("/")
def hello_world():
    return {"Hello": "World"}


@app.post("/users/")
def create_user(user: UserCreate, db: DBSession) -> User:
    db.add(User)
    db.commit()
    db.refresh(user)
    return user


@app.get("/users/")
def list_users(db: DBSession) -> list[User]:
    users = db.exec(select(User))
    return users


@app.get("/users/{id}")
def get_user(id: int, db: DBSession) -> User:
    user = db.get(User, id)
    if not user:
        raise HTTPException(status_code=404)
    return user


@app.delete("/users/{id}", status_code=204)
def delete_user(id: int, db: DBSession):
    user = db.get(User, id)
    if not user:
        raise HTTPException(status_code=404)
    db.delete(user)
    db.commit()
