from datetime import datetime

from sqlmodel import Session, desc, select

from globals.EEventState import EEventState
from globals.exceptions import ForbiddenOperationException, NotFoundException
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


def remove_bet(session: Session, bet_id: int, user_id: int):
    # get the bet from bet_id
    bet = session.exec(select(Bet).where(Bet.id == bet_id)).first()

    if bet is None:
        raise NotFoundException("Bet not found")

    # check if bet creator is the one removing it
    if bet.transactions[0].user_id != user_id:
        raise ForbiddenOperationException(
            "You cannot remove the bet if you are not the one that placed it"
        )

    # get the latest negative amount transaction
    amount = _get_bet_amount(session=session, bet_id=bet_id, user_id=user_id)

    # set all transactions foreign key to that bet to NULL
    _make_transactions_orphans(session=session, bet_id=bet_id)

    # delete the bet
    session.delete(bet)

    # create a new transaction for refunding with opposite amount to the latest negative transaction
    event = bet.outcome.market.event
    market = bet.outcome.market
    outcome = bet.outcome

    refund_transaction = Transaction(
        timestamp=int(datetime.now().timestamp()),
        description=f"Removed bet on {event.name} -> {market.name} {outcome.name}",
        amount=-amount,
        user_id=user_id,
        bet_id=None,
        bet=None,
    )

    session.add(refund_transaction)
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


def _get_bet_amount(session: Session, bet_id: int, user_id: int):
    statement = (
        select(Transaction)
        .join(Bet)
        .where(Transaction.user_id == user_id)
        .where(Transaction.bet_id == bet_id)
        .where(Transaction.amount < 0)
        .order_by(desc(Transaction.timestamp))
    )

    transaction = session.exec(statement).first()
    if transaction is None:
        raise NotFoundException()

    return transaction.amount


def _make_transactions_orphans(session: Session, bet_id: int):
    # set all transactions' fk bet_id linked to the bet to NULL

    transactions = session.exec(
        select(Transaction).where(Transaction.bet_id == bet_id)
    ).all()

    for transaction in transactions:
        transaction.bet_id = None

    session.add_all(transactions)
    session.flush()
