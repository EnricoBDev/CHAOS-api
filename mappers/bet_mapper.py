from sqlmodel import Session, desc, select

from globals.exceptions import NotFoundException
from models import Bet, BetPublic, Transaction


def bet_to_public(bet: Bet, user_id: int, session: Session) -> BetPublic:
    amount = _get_bet_amount(bet, user_id, session)
    return BetPublic(**bet.model_dump(), amount=amount)


def _get_bet_amount(bet: Bet, user_id: int, session: Session) -> int:
    # we take the last transaction that has a negative amount, since negative amount means a wager was put on an outcome and a positive amount means the wager was won
    statement = (
        select(Transaction)
        .join(Bet)
        .where(Transaction.user_id == user_id)
        .where(Transaction.bet_id == bet.id)
        .where(Transaction.amount < 0)
        .order_by(desc(Transaction.timestamp))
    )

    transaction = session.exec(statement).first()

    # this should never occour because:
    # - when we create a new bet we always create a transaction related to that
    # - when a bet is removed for sure we are going to delete the Bet table entry so this function wouldn't even be called
    if transaction is None:
        raise NotFoundException()

    # we invert the sign because the transaction created when the bet is placed
    # is negative, but we want to show a user a positive amouns (same when creating a bet)
    return -transaction.amount
