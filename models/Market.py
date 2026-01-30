from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .Event import Event
    from .Outcome import Outcome, OutcomeCreate, OutcomePublic


class MarketBase(SQLModel):
    name: str


class MarketCreate(MarketBase):
    outcomes: list["OutcomeCreate"]
    event_id: int = Field(foreign_key="event.id")


class Market(MarketBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id")

    event: "Event" = Relationship(back_populates="markets")
    outcomes: list["Outcome"] = Relationship(back_populates="market")


class MarketPublic(MarketBase):
    id: int
    open_for_bet: bool
    outcomes: list["OutcomePublic"]
