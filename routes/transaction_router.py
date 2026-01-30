from fastapi import APIRouter, Query

from auth import token
from auth.security_schema import OAuth2Dep
from globals.database import SessionDep
from globals.exceptions import InvalidTokenException, http_unauthorized_exception
from models import TransactionPublic
from service import transaction_service

router = APIRouter()


@router.get("/transactions", responses={401: {"description": "Invalid token"}})
def get_transactions(
    session: SessionDep,
    access_token: OAuth2Dep,
    limit: int = Query(default=20, le=100, ge=1),
    page: int = Query(default=0, ge=0),
) -> list[TransactionPublic]:
    try:
        user_id = token.get_id_from_token(access_token)
        transactions = transaction_service.get_transaction_history(
            session, user_id, page, limit
        )
    except InvalidTokenException:
        raise http_unauthorized_exception("Token is invalid")

    return transactions
