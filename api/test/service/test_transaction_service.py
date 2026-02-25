from sqlmodel import Session

from models import Transaction
from service.transaction_service import get_transaction_history
from test.conftest import get_current_timestamp


def test_get_transaction_history_wrong_user(mock_session_db: Session):
    user_id = 67
    assert len(get_transaction_history(session=mock_session_db, user_id=user_id)) == 0


def test_get_transaction_history_page_too_high(mock_session_db: Session):
    transaction_1 = Transaction(
        id=1000,
        description="test",
        amount=67,
        timestamp=get_current_timestamp(),
        user_id=1,
    )
    transaction_2 = Transaction(
        id=1001,
        description="test",
        amount=67,
        timestamp=get_current_timestamp(),
        user_id=1,
    )
    transaction_3 = Transaction(
        id=1002,
        description="test",
        amount=67,
        timestamp=get_current_timestamp(),
        user_id=1,
    )
    transaction_4 = Transaction(
        id=1003,
        description="test",
        amount=67,
        timestamp=get_current_timestamp(),
        user_id=1,
    )

    mock_session_db.add(transaction_1)
    mock_session_db.add(transaction_2)
    mock_session_db.add(transaction_3)
    mock_session_db.add(transaction_4)

    actual = len(
        get_transaction_history(session=mock_session_db, user_id=1, page=10, limit=1)
    )

    assert 0 == actual


def test_get_transaction_history(mock_session_db: Session):
    transaction_1 = Transaction(
        id=1000,
        description="test",
        amount=67,
        timestamp=get_current_timestamp() + 86401,
        user_id=1,
        bet_id=None,
    )
    transaction_2 = Transaction(
        id=1001,
        description="test",
        amount=67,
        timestamp=get_current_timestamp() + 86402,
        user_id=1,
        bet_id=None,
    )
    transaction_3 = Transaction(
        id=1002,
        description="test",
        amount=67,
        timestamp=get_current_timestamp() + 86403,
        user_id=1,
        bet_id=None,
    )
    transaction_4 = Transaction(
        id=1003,
        description="test",
        amount=67,
        timestamp=get_current_timestamp() + 86404,
        user_id=1,
        bet_id=None,
    )

    mock_session_db.add(transaction_1)
    mock_session_db.add(transaction_2)
    mock_session_db.add(transaction_3)
    mock_session_db.add(transaction_4)

    output = get_transaction_history(
        session=mock_session_db, user_id=1, page=1, limit=2
    )

    actual = [i.id for i in output]

    expected = [1001, 1000]

    assert actual == expected
