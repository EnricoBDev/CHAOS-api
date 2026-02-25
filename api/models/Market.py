from typing import TYPE_CHECKING

from pydantic import model_validator
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .Event import Event
    from .Outcome import Outcome, OutcomeCreate, OutcomePublic


class MarketBase(SQLModel):
    name: str


class MarketCreate(MarketBase):
    outcomes: list["OutcomeCreate"]
    event_id: int = Field(foreign_key="event.id")

    @model_validator(mode="after")
    def check_outcomes_number(self) -> "MarketCreate":
        if len(self.outcomes) < 2:
            raise ValueError("There should be at least two outcomes")
        return self


class Market(MarketBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id")

    event: "Event" = Relationship(back_populates="markets")
    outcomes: list["Outcome"] = Relationship(back_populates="market")


class MarketPublic(MarketBase):
    id: int
    open_for_bet: bool
    outcomes: list["OutcomePublic"]
