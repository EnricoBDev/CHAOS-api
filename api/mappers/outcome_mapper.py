from sqlmodel import Session, select

from mappers.bet_mapper import bet_to_public
from models import Bet, Outcome, OutcomePublic, Transaction


def outcome_to_public(
    outcome: Outcome, user_id: int, session: Session
) -> OutcomePublic:
    user_bet = _get_user_bet_on_outcome(session, user_id, outcome)
    if user_bet is None:
        user_bet_public = None
    else:
        user_bet_public = bet_to_public(user_bet, user_id, session)

    public = OutcomePublic(**outcome.model_dump(), user_bet=user_bet_public)

    return public


def _get_user_bet_on_outcome(
    session: Session, user_id: int, outcome: Outcome
) -> Bet | None:
    statement = (
        select(Bet)
        .join(Transaction)
        .join(Outcome)
        .where(Transaction.user_id == user_id)
        .where(Outcome.id == outcome.id)
    )

    return session.exec(statement).first()
