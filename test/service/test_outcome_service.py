from datetime import datetime

import pytest
from sqlmodel import Session, select

from globals.EEventState import EEventState
from globals.exceptions import ForbiddenOperationException, NotFoundException
from models import Bet, Event, Outcome, Transaction
from service.outcome_service import select_winning_outcomes


def test_select_winning_outcome_event_not_finished(mock_session_db: Session):
    outcome_id = 1
    with pytest.raises(ForbiddenOperationException):
        select_winning_outcomes(
            session=mock_session_db, winning_outcome_ids=[outcome_id], user_id=1
        )


def test_select_winning_outcome_outcome_not_exists(mock_session_db: Session):
    outcome_id = 300
    with pytest.raises(NotFoundException):
        select_winning_outcomes(
            session=mock_session_db, winning_outcome_ids=[outcome_id], user_id=1
        )


def test_select_winning_outcome_user_not_creator(mock_session_db: Session):
    with pytest.raises(
        ForbiddenOperationException, match="You are not the event creator"
    ):
        select_winning_outcomes(
            session=mock_session_db, winning_outcome_ids=[1], user_id=2
        )


def test_select_winning_outcome(mock_session_db: Session):
    outcome_id = 6
    # create a bet on outcome 6 -> market 3 -> event -> 2
    bet = Bet(id=1000, outcome_id=outcome_id)
    # create multiple transactions on that bet so that we can test if function works when refunds are made
    transaction1 = Transaction(
        id=1000,
        description="test",
        amount=-100,
        bet_id=bet.id,
        timestamp=1,
        user_id=2,
    )
    transaction2 = Transaction(
        id=1001,
        description="refund test",
        amount=100,
        bet_id=bet.id,
        timestamp=2,
        user_id=2,
    )
    transaction3 = Transaction(
        id=1002,
        description="another test",
        amount=-500,
        bet_id=bet.id,
        timestamp=2,
        user_id=2,
    )

    mock_session_db.add(bet)
    mock_session_db.add(transaction1)
    mock_session_db.add(transaction2)
    mock_session_db.add(transaction3)

    select_winning_outcomes(
        session=mock_session_db, winning_outcome_ids=[outcome_id], user_id=1
    )

    event = mock_session_db.exec(select(Event).where(Event.id == 2)).one()
    winning_outcome = mock_session_db.exec(
        select(Outcome).where(Outcome.id == outcome_id)
    ).one()
    losing_outcome = mock_session_db.exec(
        select(Outcome).where(Outcome.id == outcome_id + 1)
    ).one()
    # new transaction will have id=1003
    new_transaction = mock_session_db.exec(
        select(Transaction).where(Transaction.id == 1003)
    ).one()

    assert event.event_state == EEventState.SETTLED
    assert winning_outcome.is_winning
    assert not losing_outcome.is_winning
    assert new_transaction.amount == 1000
