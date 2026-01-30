from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .Bet import Bet
    from .User import User


class TransactionBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    description: str
    amount: int
    timestamp: int


class TransactionPublic(TransactionBase):
    user_id: int


class Transaction(TransactionBase, table=True):
    bet_id: int | None = Field(default=None, foreign_key="bet.id")
    user_id: int = Field(foreign_key="user.id")

    bet: Optional["Bet"] = Relationship(back_populates="transactions")
    user: "User" = Relationship(back_populates="transactions")
