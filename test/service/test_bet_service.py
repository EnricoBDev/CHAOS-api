import logging

import pytest
from sqlalchemy.dialects.mysql import match
from sqlalchemy.sql.functions import user
from sqlalchemy.testing.provision import get_temp_table_name
from sqlmodel import Session, select

from globals.exceptions import ForbiddenOperationException
from models import Bet, BetCreate, Outcome, Transaction
from service.bet_service import place_bet

logger = logging.getLogger(__name__)


def test_place_bet_outcome_not_exists(mock_session_db: Session):
    bet = BetCreate(outcome_id=69, amount=10)

    with pytest.raises(
        ForbiddenOperationException,
        match=r"You are placing a bet on an inexistent Outcome",
    ) as exc_info:
        place_bet(session=mock_session_db, user_id=1, bet=bet)
    logger.info(f"{exc_info.value}")


def test_place_bet_event_not_new(mock_session_db: Session):
    bet = BetCreate(outcome_id=10, amount=10)
    with pytest.raises(
        ForbiddenOperationException,
        match=r"You are placing a bet on an event that was SETTLED/REFUNDED",
    ) as exc_info:
        place_bet(session=mock_session_db, user_id=1, bet=bet)
    logger.info(f"{exc_info.value}")


def test_place_bet_user_not_exists(mock_session_db: Session):
    bet = BetCreate(outcome_id=1, amount=10)
    with pytest.raises(
        ForbiddenOperationException,
        match=r"The user that is placing the bet does not exist",
    ) as exc_info:
        place_bet(session=mock_session_db, user_id=100, bet=bet)
    logger.info(f"{exc_info.value}")


def test_place_bet_user_balance_is_enough(mock_session_db: Session):
    bet = BetCreate(outcome_id=1, amount=10000000)
    with pytest.raises(
        ForbiddenOperationException,
        match=r"You are broke! \(insert cat laughing at you GIF\)",
    ) as exc_info:
        place_bet(session=mock_session_db, user_id=2, bet=bet)
    logger.info(f"{exc_info.value}")


def test_place_bet_user_is_creator(mock_session_db: Session):
    bet = BetCreate(outcome_id=1, amount=10)
    with pytest.raises(
        ForbiddenOperationException,
        match=r"You created the event you are placing a bet on, that's cheating",
    ) as exc_info:
        place_bet(session=mock_session_db, user_id=1, bet=bet)
    logger.info(f"{exc_info.value}")


def test_place_bet_already_exists(mock_session_db: Session):
    # place a fake bet
    bet = Bet(id=1000, outcome_id=1)
    mock_session_db.add(bet)
    transaction = Transaction(
        id=1000, bet_id=1000, user_id=2, description="test", timestamp=1, amount=-10
    )
    mock_session_db.add(transaction)

    bet = BetCreate(outcome_id=1, amount=10)
    with pytest.raises(
        ForbiddenOperationException,
        match=r"You already placed a bet on this outcome",
    ) as exc_info:
        place_bet(session=mock_session_db, user_id=2, bet=bet)
    logger.info(f"{exc_info.value}")


def test_place_bet_event_has_already_started(mock_session_db: Session):
    bet = BetCreate(outcome_id=6, amount=10)
    with pytest.raises(
        ForbiddenOperationException,
        match=r"The event has already started",
    ) as exc_info:
        place_bet(session=mock_session_db, user_id=2, bet=bet)
    logger.info(f"{exc_info.value}")


def test_place_bet(mock_session_db: Session):
    bet = BetCreate(outcome_id=1, amount=10)
    place_bet(session=mock_session_db, user_id=2, bet=bet)

    # new bet will have id 1
    # new transaction will have id 3
    table_bet = mock_session_db.exec(select(Bet).where(Bet.id == 1)).one()
    table_transaction = mock_session_db.exec(
        select(Transaction).where(Transaction.id == 3)
    ).one()

    assert table_bet.outcome_id == 1
    assert table_bet.transactions[0].id == 3
    assert table_transaction.id == 3
    assert table_transaction.amount == -10
