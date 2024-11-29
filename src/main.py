from fastapi import FastAPI

from .modules.users import router as users

app = FastAPI()
app.include_router(users.router)


@app.get("/")
async def hello_world():
    return {"Hello": "World!"}
