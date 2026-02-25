from typing import TYPE_CHECKING

from pydantic import model_validator
from sqlmodel import Field, Relationship, SQLModel

from globals.EEventState import EEventState

if TYPE_CHECKING:
    from .Market import Market, MarketPublic
    from .User import User


class EventBase(SQLModel):
    name: str
    description: str
    start_timestamp: int
    end_timestamp: int

    @model_validator(mode="after")
    def check_timestamps(self) -> "EventBase":
        if self.end_timestamp < self.start_timestamp:
            raise ValueError("end_timestamp must be after start_timestamp")
        return self


class EventCreate(EventBase):
    pass


class Event(EventBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    event_state: EEventState = EEventState.NEW

    creator_id: int = Field(foreign_key="user.id")
    creator: "User" = Relationship(back_populates="created_events")
    markets: list["Market"] = Relationship(back_populates="event")


class EventPublic(EventBase):
    id: int
    event_state: EEventState
    creator_id: int
    public_markets: list["MarketPublic"]
