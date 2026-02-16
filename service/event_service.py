import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlmodel import Session, asc, select

from globals.EEventState import EEventState
from globals.exceptions import (
    ForbiddenOperationException,
    NotFoundException,
    TimezoneValidationException,
)
from mappers import event_mapper
from models import (
    Event,
    EventCreate,
    EventPublic,
    Market,
    MarketCreate,
    Outcome,
    Transaction,
)

logger = logging.getLogger("uvicorn.error")


def create_event(event: EventCreate, session: Session, user_id: int):
    table_event = Event(**event.model_dump(), creator_id=user_id)

    session.add(table_event)
    session.commit()


def add_market(market: MarketCreate, session: Session, user_id: int):
    event = _get_event_by_id(market.event_id, session)
    if event is None:
        raise NotFoundException("Parent event was not found")

    if event.creator_id != user_id:
        raise ForbiddenOperationException("You are not the event creator")

    table_market = Market(name=market.name, event_id=market.event_id, outcomes=[])

    session.add(table_market)
    session.flush()
    session.refresh(table_market)

    table_outcomes = [
        Outcome(name=outcome.name, odds=outcome.odds, market_id=table_market.id)  # ty:ignore[invalid-argument-type]
        for outcome in market.outcomes
    ]

    table_market.outcomes = table_outcomes
    session.add(table_market)

    event.markets.append(table_market)
    session.add(event)

    session.commit()


def get_today_events(
    session: Session,
    user_id: int,
    timezone: str = "UTC",
    day_offset: int = 0,
) -> list[EventPublic]:
    day_offset_timedelta = timedelta(days=day_offset)
    try:
        datetime_with_offset = (
            datetime.now(tz=ZoneInfo(timezone)) + day_offset_timedelta
        )
    except ZoneInfoNotFoundError:
        raise TimezoneValidationException("Timezone identifier string does not exist")

    end_of_day = int(
        datetime_with_offset.replace(
            hour=23, minute=59, second=59, microsecond=0
        ).timestamp()
    )
    start_of_day = int(
        datetime_with_offset.replace(
            hour=0, minute=0, second=0, microsecond=0
        ).timestamp()
    )
    logger.info(f"End day: {datetime.fromtimestamp(end_of_day, tz=ZoneInfo(timezone))}")
    logger.info(
        f"Start day: {datetime.fromtimestamp(start_of_day, tz=ZoneInfo(timezone))}"
    )

    """
    # changed this since its better to just show the events for the whole day
    # even if they have already started
    if day_offset == 0:
        timestamp_with_offset = int(datetime_with_offset.timestamp())
    else:
        timestamp_with_offset = int(
            datetime_with_offset.replace(
                hour=0, minute=0, second=0, microsecond=0
            ).timestamp()
        )
    
    logger.info(
        f"Timestamp: {datetime.fromtimestamp(timestamp_with_offset, tz=ZoneInfo(timezone))} for tz={timezone}"
    )
    logger.info(
        f"End of day: {(datetime.fromtimestamp(end_of_day, tz=ZoneInfo(timezone)))} for tz={timezone}"
    )
    """

    table_events = session.exec(
        select(Event)
        .where(Event.start_timestamp >= start_of_day)
        .where(Event.start_timestamp <= end_of_day)
        .order_by(asc(Event.start_timestamp))
    )

    public_events = [
        event_mapper.event_to_public(e, user_id, session) for e in table_events
    ]

    return public_events


def refund_event(session: Session, user_id: int, event_id: int):
    event = _get_event_by_id(session=session, event_id=event_id)

    if event is None:
        raise NotFoundException("Event was not found")

    if event.creator_id != user_id:
        raise ForbiddenOperationException("You are not the event creator")

    if event.end_timestamp > int(datetime.now().timestamp()):
        raise ForbiddenOperationException("The event is not over yet")

    event.event_state = EEventState.REFUNDED
    session.add(event)
    session.flush()

    _refund_bets(session=session, event=event)
    session.commit()


def _get_event_by_id(event_id: int, session: Session) -> Event | None:
    result = session.exec(select(Event).where(Event.id == event_id)).first()

    return result


def _refund_bets(session: Session, event: Event):
    for market in event.markets:
        for outcome in market.outcomes:
            for bet in outcome.bets:
                negative_transactions = filter(
                    lambda obj: obj.amount < 0, bet.transactions
                )
                last_negative_transaction = max(
                    negative_transactions, key=lambda obj: obj.timestamp
                )
                negative_amount = last_negative_transaction.amount
                new_transaction = Transaction(
                    timestamp=int(datetime.now().timestamp()),
                    bet_id=bet.id,
                    user_id=last_negative_transaction.user_id,
                    amount=-negative_amount,
                    description=f"Refund {-negative_amount} points for {event.name} -> {outcome.market.name} {outcome.name}",
                )
                session.add(new_transaction)
