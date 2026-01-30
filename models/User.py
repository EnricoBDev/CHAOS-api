from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .Event import Event, EventPublic
    from .Transaction import Transaction, TransactionPublic


class UserBase(SQLModel):
    username: str = Field(unique=True)
    email: EmailStr = Field(unique=True)


class UserCreate(UserBase):
    password: str


class UserPublic(UserBase):
    id: int
    balance: int | None = None
    created_events: list["EventPublic"]
    transactions: list["TransactionPublic"]


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    password: str

    created_events: list["Event"] = Relationship(back_populates="creator")
    transactions: list["Transaction"] = Relationship(back_populates="user")
