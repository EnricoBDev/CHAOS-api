from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .Bet import Bet, BetPublic
    from .Market import Market


class OutcomeBase(SQLModel):
    name: str
    odds: float = Field(ge=1)


class OutcomeCreate(OutcomeBase):
    pass


class Outcome(OutcomeBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    is_winning: int | None = None

    market_id: int = Field(foreign_key="market.id")
    market: "Market" = Relationship(back_populates="outcomes")
    bets: list["Bet"] = Relationship(back_populates="outcome")


class OutcomePublic(OutcomeBase):
    id: int
    is_winning: int | None = None
    user_bet: Optional["BetPublic"] = None
