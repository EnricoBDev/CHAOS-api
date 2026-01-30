from fastapi import APIRouter

from auth import token
from auth.security_schema import OAuth2Dep
from globals.database import SessionDep
from globals.exceptions import (
    ForbiddenOperationException,
    InvalidTokenException,
    NotFoundException,
    http_forbidden_exception,
    http_not_found_exception,
    http_unauthorized_exception,
)
from service import outcome_service

router = APIRouter()


@router.post("/winning-outcome")
def select_winning_outcomes(
    auth_token: OAuth2Dep, session: SessionDep, winning_outcome_ids: list[int]
):
    try:
        user_id = token.get_id_from_token(auth_token)
    except InvalidTokenException:
        raise http_unauthorized_exception("Token is not valid")

    try:
        outcome_service.select_winning_outcomes(
            session=session, winning_outcome_ids=winning_outcome_ids, user_id=user_id
        )
    except NotFoundException as e:
        raise http_not_found_exception(e.args[0])
    except ForbiddenOperationException as e:
        raise http_forbidden_exception(e.args[0])
