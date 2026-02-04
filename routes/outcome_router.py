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


@router.post(
    "/winning-outcome",
    responses={
        401: {"description": "Invalid token"},
        404: {"description": "Outcome not found"},
        403: {
            "description": "Forbidden Operation",
            "content": {
                "application/json": {
                    "examples": {
                        "not_creator": {
                            "summary": "User is not the event creator",
                            "value": {"detail": "You are not the event creator"},
                        },
                        "event_not_finished": {
                            "summary": "Event has not finished",
                            "value": {
                                "detail": "Cannot settle an event that has not finished"
                            },
                        },
                        "multiple_winning_outcomes_same_market": {
                            "summary": "Mutliple winning outcomes in the same market",
                            "value": {
                                "detail": "There are multiple winning outcomes that are in the same market, there can only be one for each market"
                            },
                        },
                    }
                }
            },
        },
    },
)
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
    except NotFoundException:
        raise http_not_found_exception("Outcome not found")
    except ForbiddenOperationException as e:
        raise http_forbidden_exception(e.args[0])
