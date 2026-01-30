from mappers import transaction_mapper
from models import Transaction, TransactionPublic


def test_transaction_to_public():
    transaction = Transaction(
        id=0, description="test", amount=100, timestamp=1337, bet_id=None, user_id=0
    )

    expected = TransactionPublic(
        id=0, description="test", amount=100, timestamp=1337, bet_id=None, user_id=0
    )

    actual = transaction_mapper.transaction_to_public(transaction)

    assert expected == actual
