from datetime import datetime

import pytest
from sqlmodel import Session, SQLModel, create_engine

import models  # noqa: F401
from globals.EEventState import EEventState
from models.Event import Event
from models.Market import Market
from models.Outcome import Outcome
from models.Transaction import Transaction
from models.User import User


def get_current_timestamp() -> int:
    return int(datetime.now().timestamp())


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="mock_session_db")
def mock_db_session(session: Session):
    mock_start_timestamp = get_current_timestamp() + 3600
    mock_end_timestamp = get_current_timestamp() + 7200

    user1 = User(id=1, username="creator", email="creator@mail.com", password="secret")
    user2 = User(id=2, username="gambler", email="gambler@mail.com", password="secret2")

    session.add(user1)
    session.add(user2)

    event1 = Event(
        id=1,
        name="Generico",
        description="Evento generico",
        start_timestamp=mock_start_timestamp,
        end_timestamp=mock_end_timestamp,
        creator_id=1,
        event_state=EEventState.NEW,
    )
    event2 = Event(
        id=2,
        name="Terminato",
        description="Evento terminato",
        start_timestamp=mock_start_timestamp - 3660,
        end_timestamp=mock_end_timestamp - 7260,
        creator_id=1,
        event_state=EEventState.NEW,
    )
    event3 = Event(
        id=3,
        name="To Settle",
        description="Evento da settle",
        start_timestamp=mock_start_timestamp - 3660,
        end_timestamp=mock_end_timestamp - 7260,
        creator_id=1,
        event_state=EEventState.SETTLED,
    )
    event4 = Event(
        id=4,
        name="To Refund",
        description="Evento da refund",
        start_timestamp=mock_start_timestamp - 3660,
        end_timestamp=mock_end_timestamp - 7260,
        creator_id=1,
        event_state=EEventState.REFUNDED,
    )
    event5 = Event(
        id=5,
        name="Vuoto",
        description="Evento senza mercati",
        start_timestamp=mock_start_timestamp,
        end_timestamp=mock_end_timestamp,
        creator_id=1,
        event_state=EEventState.NEW,
    )
    event6 = Event(
        id=6,
        name="Fixed timestamp",
        description="Event with fixed timestamps",
        start_timestamp=100,
        end_timestamp=200,
        creator_id=1,
        event_state=EEventState.NEW,
    )

    session.add(event1)
    session.add(event2)
    session.add(event3)
    session.add(event4)
    session.add(event5)
    session.add(event6)

    market1 = Market(id=1, name="GOAL", event_id=1)
    market2 = Market(id=2, name="OVER 1.5", event_id=1)
    market3 = Market(id=3, name="GOAL", event_id=2)
    market4 = Market(id=4, name="OVER 1.5", event_id=2)
    market5 = Market(id=5, name="GOAL", event_id=3)
    market6 = Market(id=6, name="OVER 1.5", event_id=3)
    market7 = Market(id=7, name="GOAL", event_id=4)
    market8 = Market(id=8, name="OVER 1.5", event_id=4)

    session.add(market1)
    session.add(market2)
    session.add(market3)
    session.add(market4)
    session.add(market5)
    session.add(market6)
    session.add(market7)
    session.add(market8)

    outcome1 = Outcome(id=1, name="YES", odds=2.0, market_id=1)
    outcome3 = Outcome(id=3, name="NO", odds=3.0, market_id=1)
    outcome4 = Outcome(id=4, name="YES", odds=2.0, market_id=2)
    outcome5 = Outcome(id=5, name="NO", odds=3.0, market_id=2)
    outcome6 = Outcome(id=6, name="YES", odds=2.0, market_id=3)
    outcome7 = Outcome(id=7, name="NO", odds=3.0, market_id=3)
    outcome8 = Outcome(id=8, name="YES", odds=2.0, market_id=4)
    outcome9 = Outcome(id=9, name="NO", odds=3.0, market_id=4)
    outcome10 = Outcome(id=10, name="YES", odds=2.0, market_id=5)
    outcome11 = Outcome(id=11, name="NO", odds=3.0, market_id=5)
    outcome12 = Outcome(id=12, name="YES", odds=2.0, market_id=6)
    outcome13 = Outcome(id=13, name="NO", odds=3.0, market_id=6)
    outcome14 = Outcome(id=14, name="YES", odds=2.0, market_id=7)
    outcome15 = Outcome(id=15, name="NO", odds=3.0, market_id=7)
    outcome16 = Outcome(id=16, name="YES", odds=2.0, market_id=8)
    outcome17 = Outcome(id=17, name="NO", odds=3.0, market_id=8)

    session.add(outcome1)
    session.add(outcome3)
    session.add(outcome4)
    session.add(outcome5)
    session.add(outcome6)
    session.add(outcome7)
    session.add(outcome8)
    session.add(outcome9)
    session.add(outcome10)
    session.add(outcome11)
    session.add(outcome12)
    session.add(outcome13)
    session.add(outcome14)
    session.add(outcome15)
    session.add(outcome16)
    session.add(outcome17)

    transaction1 = Transaction(
        id=1,
        description="Initial transaction",
        amount=1000,
        timestamp=get_current_timestamp(),
        user_id=1,
    )
    transaction2 = Transaction(
        id=2,
        description="Initial transaction",
        amount=1000,
        timestamp=get_current_timestamp(),
        user_id=2,
    )

    session.add(transaction1)
    session.add(transaction2)

    session.commit()
    yield session
