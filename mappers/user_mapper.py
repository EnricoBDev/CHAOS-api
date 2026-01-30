from sqlmodel import Session

from mappers import event_mapper, transaction_mapper
from models import User, UserPublic


def user_to_public(user: User, session: Session) -> UserPublic:
    public_events = [
        event_mapper.event_to_public(e, user.id, session)  # ty:ignore[invalid-argument-type]
        for e in user.created_events
    ]

    public_transactions = [
        transaction_mapper.transaction_to_public(t) for t in user.transactions
    ]

    balance = _calculate_balance(user)

    public = UserPublic(
        **user.model_dump(exclude={"created_events"}),
        created_events=public_events,
        transactions=public_transactions,
        balance=balance,
    )

    return public


def _calculate_balance(user: User) -> int:
    balance = 0
    for t in user.transactions:
        balance += t.amount

    return balance
