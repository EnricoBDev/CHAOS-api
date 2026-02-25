import logging
from datetime import datetime

import pytest
from sqlmodel import Session, select

from globals.exceptions import ForbiddenOperationException, NotFoundException
from models import Bet, BetCreate, Outcome, Transaction
from service.bet_service import place_bet, remove_bet

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


def test_remove_bet_not_found(mock_session_db: Session):
    with pytest.raises(NotFoundException, match="Bet not found"):
        remove_bet(session=mock_session_db, bet_id=777, user_id=2)


def test_remove_bet_user_not_better(mock_session_db: Session):
    # create a new bet
    new_transaction = Transaction(
        id=67,
        amount=-100,
        description="test",
        timestamp=int(datetime.now().timestamp()),
        bet_id=67,
        user_id=2,
    )
    new_bet = Bet(id=67, outcome_id=17)
    mock_session_db.add(new_bet)
    mock_session_db.add(new_transaction)

    with pytest.raises(
        ForbiddenOperationException,
        match="You cannot remove the bet if you are not the one that placed it",
    ):
        remove_bet(session=mock_session_db, user_id=1, bet_id=67)


def test_remove_bet(mock_session_db: Session):
    # create a new bet
    new_transaction = Transaction(
        id=67,
        amount=-100,
        description="test",
        timestamp=int(datetime.now().timestamp()),
        bet_id=67,
        user_id=2,
    )
    new_bet = Bet(id=67, outcome_id=17)
    mock_session_db.add(new_bet)
    mock_session_db.add(new_transaction)

    remove_bet(session=mock_session_db, bet_id=67, user_id=2)

    # the refunded transaction will be the only one with amount=100 on user_id=2
    refunded_transaction = mock_session_db.exec(
        select(Transaction)
        .where(Transaction.amount == 100)
        .where(Transaction.user_id == 2)
    ).first()

    logger.info(f"Refunded transaction amount: {refunded_transaction.amount}")  # ty:ignore[unresolved-attribute]

    assert refunded_transaction is not None

    # check if the transaction we created earlier has no bet_id
    mock_session_db.refresh(new_transaction)
    assert new_transaction.bet_id is None

    # check that there is no bet with id=67
    deleted_bet = mock_session_db.exec(select(Bet).where(Bet.id == 67)).first()
    assert deleted_bet is None
