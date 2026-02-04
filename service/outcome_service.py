from datetime import datetime

from sqlmodel import Session, desc, select

from globals.EEventState import EEventState
from globals.exceptions import ForbiddenOperationException, NotFoundException
from models import (
    Bet,
    Event,
    Market,
    Outcome,
    Transaction,
    User,
)


def select_winning_outcomes(
    session: Session, winning_outcome_ids: list[int], user_id: int
):
    """
    - set the event as SETTLED
    - set for every outcome whose id is in winning_outcome_ids, set is_winning to true
      and set is_winning for the other outcomes in the same market to false
    - take every bet placed on every winning outcome. get the last transaction
      with a negative amount linked to the bet, multiply the amount by the odd and
      create a new transaction with that value
    """

    if _check_multiple_outcomes_same_market(
        session=session, outcome_id_list=winning_outcome_ids
    ):
        raise ForbiddenOperationException(
            "There are multiple winning outcomes in the same market"
        )

    for outcome_id in winning_outcome_ids:
        outcome_event = _get_outcome_event(session=session, outcome_id=outcome_id)

        if outcome_event is None:
            raise NotFoundException("Event relative to the outcome was not found")

        if outcome_event.creator_id != user_id:
            raise ForbiddenOperationException("You are not the event creator")

        current_timestamp = int(datetime.now().timestamp())
        if outcome_event.end_timestamp > current_timestamp:
            raise ForbiddenOperationException(
                "Cannot settle an event that has not finished"
            )

        _set_event_to_settled(session=session, outcome_id=outcome_id)
        _set_is_winning(session=session, outcome_id=outcome_id)
        _pay_bets(session=session, outcome_id=outcome_id)


def _set_event_to_settled(session: Session, outcome_id: int):
    event = _get_outcome_event(session=session, outcome_id=outcome_id)

    if event is None:
        raise NotFoundException("Event relative to the outcome was not found")

    event.event_state = EEventState.SETTLED

    session.add(event)
    session.commit()


def _set_is_winning(session: Session, outcome_id: int):
    market = session.exec(
        select(Market).join(Outcome).where(Outcome.id == outcome_id),
    ).first()

    if market is None:
        raise NotFoundException("Market relative to the outcome was not found")

    for outcome in market.outcomes:
        if outcome.id == outcome_id:
            outcome.is_winning = True
        else:
            outcome.is_winning = False

    session.add(market)
    session.commit()


def _pay_bets(session: Session, outcome_id: int):
    outcome = session.exec(select(Outcome).where(Outcome.id == outcome_id)).first()

    if outcome is None:
        raise NotFoundException("Outcome not found")

    for bet in outcome.bets:
        payout = -_get_bet_amount(session=session, bet=bet) * outcome.odds
        user_id = _get_user_id_from_bet(session=session, bet=bet)
        description = _get_payout_transaction_description(session=session, bet=bet)
        transaction = Transaction(
            description=description,
            amount=int(payout),
            timestamp=int(datetime.now().timestamp()),
            bet_id=bet.id,
            user_id=user_id,
        )
        session.add(transaction)

    session.commit()


def _get_bet_amount(session: Session, bet: Bet) -> int:
    latest_transaction = session.exec(
        select(Transaction)
        .join(Bet)
        .where(Bet.id == bet.id)
        .where(Transaction.amount < 0)
        .order_by(desc(Transaction.timestamp))
    ).first()

    if latest_transaction is None:
        raise NotFoundException("Transaction for bet on outcome not found")

    return latest_transaction.amount


def _get_user_id_from_bet(session: Session, bet: Bet) -> int:
    user_id = session.exec(
        select(User.id).join(Transaction).where(Transaction.bet_id == bet.id)
    ).first()

    if user_id is None:
        raise NotFoundException("User was not found")

    return user_id


def _get_payout_transaction_description(session: Session, bet: Bet) -> str:
    outcome = session.exec(
        select(Outcome).join(Bet).where(Bet.id == bet.id),
    ).first()

    if outcome is None:
        raise NotFoundException("Outcome not found")

    market = outcome.market
    event = market.event

    description = f"Won bet for {event.name} -> {market.name} {outcome.name}"

    return description


def _get_outcome_event(session: Session, outcome_id: int):
    event = session.exec(
        select(Event).join(Market).join(Outcome).where(Outcome.id == outcome_id),
    ).first()

    return event


def _check_multiple_outcomes_same_market(session: Session, outcome_id_list: list[int]):
    for outcome_id in outcome_id_list:
        market = session.exec(
            select(Market).join(Outcome).where(Outcome.id == outcome_id)
        ).first()

        if market is None:
            raise NotFoundException("Market not found")

        market_outcome_id_set = set(map(lambda out: out.id, market.outcomes))
        common_elements = set(outcome_id_list).intersection(market_outcome_id_set)

        if len(common_elements) > 1:
            return True

    return False
