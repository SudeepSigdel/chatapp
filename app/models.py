from sqlmodel import Column, SQLModel, Field, TIMESTAMP, text
from pydantic import EmailStr
from datetime import datetime
from fastapi import WebSocket


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True)
    password: str


class UserCreate(UserBase):
    name: str


class UserResponse(SQLModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime


class User(UserBase, table=True):
    __tablename__ = "users"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime | None = Field(default_factory=datetime.utcnow, sa_column=Column(
        TIMESTAMP(timezone=True), server_default=text("now()")))
    name: str = Field(nullable=False)


class TokenResponse(SQLModel):
    access_token: str
    token_type: str


class Connection():
    def __init__(self, websocket: WebSocket, user_id, username:str):
        self.websocket= websocket
        self.user_id= user_id
        self.username= username
