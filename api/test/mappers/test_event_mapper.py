from sqlmodel import Session, select

from globals.EEventState import EEventState
from mappers.event_mapper import event_to_public
from models import Event, EventPublic
from test.conftest import get_current_timestamp


def test_event_mapper(mock_session_db: Session):
    expected = EventPublic(
        id=6,
        name="Fixed timestamp",
        description="Event with fixed timestamps",
        start_timestamp=100,
        end_timestamp=200,
        creator_id=1,
        event_state=EEventState.NEW,
        public_markets=[],
    )

    event = mock_session_db.exec(select(Event).where(Event.id == 6)).one()
    actual = event_to_public(event=event, user_id=2, session=mock_session_db)

    assert expected == actual
