from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from sqlmodel import Session, select

from globals.EEventState import EEventState
from globals.exceptions import (
    ForbiddenOperationException,
    NotFoundException,
    TimezoneValidationException,
)
from models import (
    Event,
    EventCreate,
    Market,
    MarketCreate,
    Outcome,
    OutcomeCreate,
)
from service.event_service import (
    add_market,
    create_event,
    get_event_by_id,
    get_today_events,
)
from test.conftest import get_current_timestamp


def test_create_event(mock_session_db: Session):
    event_create = EventCreate(
        name="test",
        description="test",
        start_timestamp=1,
        end_timestamp=2,
    )

    create_event(
        event=event_create,
        session=mock_session_db,
        user_id=1,
    )

    # new Event will have id=7
    db_event = mock_session_db.exec(select(Event).where(Event.id == 7)).one()

    expected_event = Event(
        id=7,
        name="test",
        description="test",
        event_state=EEventState.NEW,
        creator_id=1,
        start_timestamp=1,
        end_timestamp=2,
    )

    assert db_event == expected_event


def test_add_market_fail_event_not_found(mock_session_db: Session):
    market = MarketCreate(
        name="test",
        outcomes=[
            OutcomeCreate(name="outcome1", odds=5),
            OutcomeCreate(name="outcome2", odds=5),
        ],
        event_id=67,
    )

    with pytest.raises(NotFoundException):
        add_market(market=market, session=mock_session_db, user_id=1)


def test_add_market_fail_not_creator(mock_session_db: Session):
    market = MarketCreate(
        name="test",
        outcomes=[
            OutcomeCreate(name="outcome1", odds=5),
            OutcomeCreate(name="outcome2", odds=5),
        ],
        event_id=1,
    )

    user_id = 2

    with pytest.raises(ForbiddenOperationException):
        add_market(market=market, session=mock_session_db, user_id=user_id)


def test_add_market(mock_session_db: Session):
    market_create = MarketCreate(
        name="test",
        event_id=1,
        outcomes=[
            OutcomeCreate(name="outcome1", odds=1.2),
            OutcomeCreate(name="outcome2", odds=1.2),
        ],
    )

    add_market(market=market_create, session=mock_session_db, user_id=1)

    # the new market will have id=9
    created_market = mock_session_db.exec(select(Market).where(Market.id == 9)).one()

    expected_outcomes = [
        Outcome(
            id=18,
            is_winning=None,
            market_id=9,
            odds=1.2,
            name="outcome1",
        ),
        Outcome(
            id=19,
            is_winning=None,
            market_id=9,
            odds=1.2,
            name="outcome2",
        ),
    ]
    expected = Market(
        id=9,
        name="test",
        event_id=1,
    )

    assert created_market == expected
    assert created_market.outcomes == expected_outcomes


def test_get_event_by_id_not_found(mock_session_db: Session):
    actual = get_event_by_id(event_id=10000, session=mock_session_db)

    assert actual is None


def test_get_event_by_id(mock_session_db: Session):
    expected = Event(
        id=6,
        name="Fixed timestamp",
        description="Event with fixed timestamps",
        start_timestamp=100,
        end_timestamp=200,
        creator_id=1,
        event_state=EEventState.NEW,
    )

    actual = get_event_by_id(event_id=6, session=mock_session_db)

    assert expected == actual


def test_get_today_events(mock_session_db: Session):
    actual = get_today_events(session=mock_session_db, user_id=2, day_offset=0)

    id_list = [event.id for event in actual]
    assert 5 == len(actual)
    # event 6 has fixed timestamps
    assert 6 not in id_list


def test_get_today_events_with_offset(mock_session_db: Session):
    offset = 1
    start = get_current_timestamp() + 86400 + 10  # +1 day + 10 seconds buffer

    event = Event(
        id=7,
        name="test",
        description="test",
        start_timestamp=start,
        end_timestamp=start + 60,
        creator_id=1,
        event_state=EEventState.NEW,
    )

    mock_session_db.add(event)

    actual = get_today_events(
        session=mock_session_db,
        user_id=2,
        day_offset=offset,
    )

    assert 1 == len(actual)
    assert 7 == actual[0].id


def test_get_today_events_ending_different_day(mock_session_db: Session):
    start = get_current_timestamp() + 86400  # +1 day
    end = start + 86400 * 2 + 10  # +2 day + 10 seconds buffer
    event = Event(
        id=7,
        name="test",
        description="test",
        start_timestamp=start,
        end_timestamp=end,
        creator_id=1,
        event_state=EEventState.NEW,
    )

    mock_session_db.add(event)

    actual = get_today_events(
        session=mock_session_db,
        user_id=2,
        day_offset=1,
    )

    assert 1 == len(actual)
    assert 7 == actual[0].id


def test_get_today_events_invalid_tz(mock_session_db: Session):
    with pytest.raises(TimezoneValidationException):
        get_today_events(
            session=mock_session_db, user_id=2, day_offset=0, timezone="asfd"
        )


def test_get_today_events_tz(mock_session_db: Session):
    tz_name = "America/New_York"
    tz = ZoneInfo(tz_name)
    now_tz = datetime.now(tz)

    # Calculate a target time near the end of the day in the specified timezone (23:58)
    target_dt = now_tz.replace(hour=23, minute=58, second=0, microsecond=0)
    event_near_end_timestamp = int(target_dt.timestamp())

    # Determine if the event should be found:
    # It must be in the future relative to 'now' because get_today_events filters for start_timestamp >= now
    should_be_found = now_tz < target_dt

    event_end_of_day = Event(
        id=100,
        name="Near End of Day",
        description="Near End of Day",
        start_timestamp=event_near_end_timestamp,
        end_timestamp=event_near_end_timestamp + 60,
        creator_id=1,
        event_state=EEventState.NEW,
    )

    # Create an event that is clearly tomorrow in the specified timezone
    tomorrow_dt = (now_tz + timedelta(days=1)).replace(hour=1, minute=0)
    event_tomorrow_timestamp = int(tomorrow_dt.timestamp())

    event_tomorrow = Event(
        id=101,
        name="Tomorrow",
        description="Tomorrow",
        start_timestamp=event_tomorrow_timestamp,
        end_timestamp=event_tomorrow_timestamp + 60,
        creator_id=1,
        event_state=EEventState.NEW,
    )

    mock_session_db.add(event_end_of_day)
    mock_session_db.add(event_tomorrow)

    actual = get_today_events(
        session=mock_session_db, user_id=2, day_offset=0, timezone=tz_name
    )
    actual_ids = [e.id for e in actual]

    if should_be_found:
        assert 100 in actual_ids
    else:
        assert 100 not in actual_ids

    assert 101 not in actual_ids
