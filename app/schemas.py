from typing import Literal

from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class User(UserBase):
    password: str


class UserInDB(UserBase):
    hashed_password: str
    role: str = "guest"


class UserRegister(UserBase):
    password: str
    role: Literal["admin", "user", "guest"] = "guest"


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TodoCreate(BaseModel):
    title: str
    description: str = ""


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class Todo(BaseModel):
    id: int
    title: str
    description: str
    completed: bool = False


class Message(BaseModel):
    message: str
