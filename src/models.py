from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    name: str
    email: str


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class UserCreate(UserBase):
    pass
