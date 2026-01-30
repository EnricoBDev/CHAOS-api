from datetime import datetime

from sqlmodel import Session, select

from globals.EEventState import EEventState
from globals.exceptions import ForbiddenOperationException
from models import Bet, BetCreate, Outcome, Transaction, User


def place_bet(session: Session, user_id: int, bet: BetCreate):
    # check if Outcome exists
    outcome = session.exec(select(Outcome).where(bet.outcome_id == Outcome.id)).first()

    if outcome is None:
        raise ForbiddenOperationException(
            "You are placing a bet on an inexistent Outcome"
        )

    event = outcome.market.event

    # check if the event is NEW
    if event.event_state != EEventState.NEW:
        raise ForbiddenOperationException(
            "You are placing a bet on an event that was SETTLED/REFUNDED"
        )

    # check if user exists
    balance = _get_user_balance(session=session, user_id=user_id)
    if balance is None:
        raise ForbiddenOperationException(
            "The user that is placing the bet does not exist"
        )

    # check if user balance is enough to place a bet
    if balance < bet.amount:
        raise ForbiddenOperationException(
            "You are broke! (insert cat laughing at you GIF)"
        )

    # check if user is not the creator of the event
    if event.creator_id == user_id:
        raise ForbiddenOperationException(
            "You created the event you are placing a bet on, that's cheating"
        )

    # check if a bet exists on an outcome
    if _check_existent_user_bet_on_outcome(outcome, user_id, session):
        raise ForbiddenOperationException("You already placed a bet on this outcome")

    # check if the event has not started
    current_timestamp = int(datetime.now().timestamp())

    if event.start_timestamp < current_timestamp:
        raise ForbiddenOperationException("The event has already started")

    # create a bet on that outcome
    table_bet = Bet.model_validate(bet)
    session.add(table_bet)
    session.flush()
    session.refresh(table_bet)

    # create a new transaction with the amount
    description = f"{bet.amount} points bet on {event.name} -> {outcome.market.name} {outcome.name}"
    transaction = Transaction(
        description=description,
        amount=-bet.amount,
        timestamp=current_timestamp,
        bet_id=table_bet.id,
        user_id=user_id,
    )

    session.add(transaction)

    session.commit()


def _check_existent_user_bet_on_outcome(
    outcome: Outcome, user_id: int, session: Session
) -> bool:
    statement = (
        select(Bet)
        .join(Transaction)
        .where(Transaction.user_id == user_id)
        .where(Bet.outcome_id == outcome.id)
    )

    result = session.exec(statement).first()

    if result is not None:
        return True

    return False


def _get_user_balance(session: Session, user_id: int) -> int | None:
    user = session.exec(
        select(User).where(User.id == user_id),
    ).first()

    if user is None:
        return None

    balance = 0
    for transaction in user.transactions:
        balance += transaction.amount

    return balance
