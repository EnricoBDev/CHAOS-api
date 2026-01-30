from sqlmodel import Session, desc, select

from mappers import transaction_mapper
from models import Transaction, TransactionPublic


def get_transaction_history(
    session: Session,
    user_id: int,
    page: int = 0,
    limit: int = 20,
) -> list[TransactionPublic]:
    statement = (
        select(Transaction)
        .where(Transaction.user_id == user_id)
        .order_by(desc(Transaction.timestamp))
        .limit(limit)
        .offset(page * limit)
    )

    result = session.exec(statement)

    public_transactions = [transaction_mapper.transaction_to_public(t) for t in result]

    return public_transactions
