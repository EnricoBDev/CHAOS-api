from sqlmodel import Session, select

from mappers.user_mapper import user_to_public
from models import Transaction, User, UserPublic


def test_user_to_public(mock_session_db: Session):
    initial_transaction = mock_session_db.exec(
        select(Transaction).where(Transaction.user_id == 2)
    ).one()

    transactions = [
        Transaction(
            id=100,
            description="Test",
            amount=-100,
            bet_id=None,
            user_id=2,
            timestamp=6969,
        ),
        Transaction(
            id=101,
            description="Test 2",
            amount=500,
            bet_id=None,
            user_id=2,
            timestamp=7070,
        ),
    ]

    mock_session_db.add_all(transactions)

    expected = UserPublic(
        id=2,
        username="gambler",
        email="gambler@mail.com",
        balance=1400,
        created_events=[],
        transactions=[initial_transaction, *transactions],
    )

    user = mock_session_db.exec(select(User).where(User.id == 2)).one()
    actual = user_to_public(user=user, session=mock_session_db)

    assert expected == actual
