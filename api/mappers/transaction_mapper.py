from models import Transaction, TransactionPublic


def transaction_to_public(transaction: Transaction) -> TransactionPublic:
    return TransactionPublic(
        id=transaction.id,
        description=transaction.description,
        amount=transaction.amount,
        timestamp=transaction.timestamp,
        user_id=transaction.user_id,
    )
