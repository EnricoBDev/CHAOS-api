from sqlmodel import Session, select

from mappers.bet_mapper import bet_to_public
from mappers.market_mapper import market_to_public
from models import Bet, Market, MarketPublic, OutcomePublic, Transaction


def test_existent_bet(mock_session_db: Session):
    transaction = Transaction(
        id=100, description="100", timestamp=1, bet_id=1, user_id=2, amount=-100
    )
    existent_bet = Bet(
        id=1,
        outcome_id=1,
        transactions=[transaction],
    )
    mock_session_db.add(existent_bet)

    user_bet = bet_to_public(bet=existent_bet, user_id=2, session=mock_session_db)
    expected = MarketPublic(
        id=1,
        name="GOAL",
        open_for_bet=False,
        outcomes=[
            OutcomePublic(
                id=1,
                name="YES",
                is_winning=None,
                odds=2.0,
                user_bet=user_bet,
            ),
            OutcomePublic(
                id=3,
                name="NO",
                is_winning=None,
                odds=3.0,
                user_bet=None,
            ),
        ],
    )

    market = mock_session_db.exec(select(Market).where(Market.id == 1)).one()
    actual = market_to_public(market=market, user_id=2, session=mock_session_db)

    assert expected == actual


def test_creator_is_gambler(mock_session_db: Session):
    expected = MarketPublic(
        id=1,
        name="GOAL",
        open_for_bet=False,
        outcomes=[
            OutcomePublic(id=1, name="YES", is_winning=None, odds=2.0, user_bet=None),
            OutcomePublic(id=3, name="NO", is_winning=None, odds=3.0, user_bet=None),
        ],
    )

    market = mock_session_db.exec(select(Market).where(Market.id == 1)).one()
    actual = market_to_public(market=market, user_id=1, session=mock_session_db)

    assert expected == actual


def test_event_started(mock_session_db: Session):
    expected = MarketPublic(
        id=3,
        name="GOAL",
        open_for_bet=False,
        outcomes=[
            OutcomePublic(id=6, name="YES", is_winning=None, odds=2.0, user_bet=None),
            OutcomePublic(id=7, name="NO", is_winning=None, odds=3.0, user_bet=None),
        ],
    )

    market = mock_session_db.exec(select(Market).where(Market.id == 3)).one()
    actual = market_to_public(market=market, user_id=2, session=mock_session_db)

    assert expected == actual


def test_event_not_new(mock_session_db: Session):
    expected = MarketPublic(
        id=5,
        name="GOAL",
        open_for_bet=False,
        outcomes=[
            OutcomePublic(id=10, name="YES", is_winning=None, odds=2.0, user_bet=None),
            OutcomePublic(id=11, name="NO", is_winning=None, odds=3.0, user_bet=None),
        ],
    )

    market = mock_session_db.exec(select(Market).where(Market.id == 5)).one()
    actual = market_to_public(market=market, user_id=2, session=mock_session_db)

    assert expected == actual


def test_open_for_bet_yes(mock_session_db: Session):
    expected = MarketPublic(
        id=1,
        name="GOAL",
        open_for_bet=True,
        outcomes=[
            OutcomePublic(id=1, name="YES", is_winning=None, odds=2.0, user_bet=None),
            OutcomePublic(id=3, name="NO", is_winning=None, odds=3.0, user_bet=None),
        ],
    )

    market = mock_session_db.exec(select(Market).where(Market.id == 1)).one()
    actual = market_to_public(market=market, user_id=2, session=mock_session_db)

    assert expected == actual
