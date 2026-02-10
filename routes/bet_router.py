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
from models import BetCreate
from service import bet_service

router = APIRouter()


@router.post(
    "/bet",
    responses={
        401: {"description": "Invalid token"},
        403: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "examples": {
                        "inexistent_outcome": {
                            "summary": "Outcome does not exist",
                            "value": {
                                "detail": "You are placing a bet on an inexistent Outcome"
                            },
                        },
                        "low_balance": {
                            "summary": "Balance is too low to place a bet",
                            "value": {
                                "detail": "You are broke! (insert cat laughing at you GIF)"
                            },
                        },
                        "event_settled_refunded": {
                            "summary": "Bet placed on a SETTLED/REFUNDED event",
                            "value": {
                                "detail": "You are placing a bet on an event that was SETTLED/REFUNDED"
                            },
                        },
                        "user_is_creator": {
                            "summary": "User is the creator of the event",
                            "value": {
                                "detail": "You created the event you are placing a bet on, that's cheating"
                            },
                        },
                        "existent_user_bet": {
                            "summary": "User already placed a bet on this outcome",
                            "value": {
                                "detail": "You already placed a bet on this outcome"
                            },
                        },
                        "event_started": {
                            "summary": "The event has already started",
                            "value": {"detail": "The event has already started"},
                        },
                    }
                }
            },
        },
    },
)
def place_bet(session: SessionDep, access_token: OAuth2Dep, bet: BetCreate):
    try:
        user_id = token.get_id_from_token(access_token)
    except InvalidTokenException:
        raise http_unauthorized_exception("Token is invalid")

    try:
        bet_service.place_bet(session=session, user_id=user_id, bet=bet)
    except ForbiddenOperationException as e:
        raise http_forbidden_exception(e.args[0])


@router.delete(
    "/bet",
    responses={
        401: {"description": "Invalid token"},
        404: {"description": "Bet not found"},
        403: {
            "description": "You cannot remove the bet if you are not the one that placed it"
        },
    },
)
def delete_bet(session: SessionDep, access_token: OAuth2Dep, bet_id: int):
    try:
        user_id = token.get_id_from_token(access_token)
    except InvalidTokenException:
        raise http_forbidden_exception("Token is invalid")

    try:
        bet_service.remove_bet(session=session, bet_id=bet_id, user_id=user_id)
    except NotFoundException as e:
        raise http_not_found_exception(e.args[0])
    except ForbiddenOperationException as e:
        raise http_forbidden_exception(e.args[0])
