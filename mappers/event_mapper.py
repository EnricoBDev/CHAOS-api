from sqlmodel import Session

from mappers import market_mapper
from models import Event, EventPublic


def event_to_public(event: Event, user_id: int, session: Session) -> EventPublic:
    public_markets = [
        market_mapper.market_to_public(m, user_id, session) for m in event.markets
    ]
    public = EventPublic(**event.model_dump(), public_markets=public_markets)

    return public
