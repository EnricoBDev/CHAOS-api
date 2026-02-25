from datetime import datetime

from sqlmodel import Session, select

from globals.EEventState import EEventState
from mappers import outcome_mapper
from models import Bet, Event, Market, MarketPublic, Outcome, Transaction


def market_to_public(market: Market, user_id: int, session: Session) -> MarketPublic:
    if (
        # --------
        # the first check could be avoided by generating the OutcomePublic list
        # first and checking if there is a user_bet placed on an Outcome by this User
        not _check_existent_bet_on_market(market, user_id, session)
        # --------
        and _check_valid_event_state(market.event)
        and market.event.creator_id != user_id
        and not _check_event_has_started(market.event)
    ):
        open_for_bet = True
    else:
        open_for_bet = False

    public_outcomes = [
        outcome_mapper.outcome_to_public(o, user_id, session) for o in market.outcomes
    ]

    public = MarketPublic(
        **market.model_dump(),
        open_for_bet=open_for_bet,
        outcomes=public_outcomes,
    )

    return public


def _check_existent_bet_on_market(
    market: Market, user_id: int, session: Session
) -> bool:
    statement = (
        select(Bet)
        .join(Transaction)
        .join(Outcome)
        .where(Transaction.user_id == user_id)
        .where(Outcome.market_id == market.id)
    )

    result = session.exec(statement).first()

    if result is not None:
        return True

    return False


def _check_valid_event_state(event: Event) -> bool:
    return event.event_state == EEventState.NEW


def _check_event_has_started(event: Event) -> bool:
    return event.start_timestamp < int(datetime.now().timestamp())
