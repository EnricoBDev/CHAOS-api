from sqlmodel import Session

from mappers.outcome_mapper import outcome_to_public
from models import Bet, BetPublic, Outcome, OutcomePublic, Transaction


def test_outcome_to_public_no_bet(mock_session_db: Session):
    outcome = Outcome(id=100, name="test", odds=1.0, is_winning=1, market_id=1)

    expected = OutcomePublic(id=100, name="test", odds=1.0, is_winning=1, user_bet=None)

    # for this test case session and user id aren't used, i coul've put anything
    actual = outcome_to_public(outcome, 2, mock_session_db)

    assert expected == actual


def test_outcome_to_public_with_bet(mock_session_db: Session):
    outcome = Outcome(id=1, name="YES", odds=2.0, market_id=1)
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

    expected = OutcomePublic(
        id=1,
        name="YES",
        odds=2.0,
        market_id=1,
        user_bet=BetPublic(id=1, amount=420, outcome_id=1),
    )

    actual = outcome_to_public(outcome, 2, mock_session_db)

    assert actual == expected
