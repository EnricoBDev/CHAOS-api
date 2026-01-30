from sqlmodel import Session

from mappers.bet_mapper import bet_to_public
from models import Bet, BetPublic, Transaction


def test_bet_to_public(mock_session_db: Session):
    new_bet = Bet(
        id=1,
        outcome_id=1,
        transactions=[
            Transaction(
                id=100, description="Test", user_id=2, timestamp=1, amount=-69, bet_id=1
            ),
            Transaction(
                id=101,
                description="Refund test",
                user_id=2,
                timestamp=2,
                amount=69,
                bet_id=1,
            ),
            Transaction(
                id=102,
                description="Test 2",
                user_id=2,
                timestamp=3,
                amount=-420,
                bet_id=1,
            ),
        ],
    )

    mock_session_db.add(new_bet)

    expected = BetPublic(id=1, outcome_id=1, amount=420)
    actual = bet_to_public(new_bet, 2, mock_session_db)

    assert expected == actual
