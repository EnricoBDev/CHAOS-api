from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .Outcome import Outcome
    from .Transaction import Transaction


class BetBase(SQLModel):
    outcome_id: int = Field(foreign_key="outcome.id")


class BetCreate(BetBase):
    amount: int = Field(gt=1)


class BetPublic(BetCreate):
    id: int


class Bet(BetBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    outcome: "Outcome" = Relationship(back_populates="bets")
    transactions: list["Transaction"] = Relationship(back_populates="bet")
