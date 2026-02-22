from fastapi import APIRouter
from pydantic_extra_types.timezone_name import TimeZoneName

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
from models import EventCreate, EventPublic, MarketCreate
from service import event_service

router = APIRouter()


@router.post("/event", responses={401: {"description": "Invalid token"}})
def create_new_event(event: EventCreate, session: SessionDep, access_token: OAuth2Dep):
    try:
        user_id = token.get_id_from_token(access_token)
        event_service.create_event(event, session, user_id)
    except InvalidTokenException:
        raise http_unauthorized_exception("Token is invalid")


@router.post(
    "/market",
    responses={
        401: {"description": "Invalid token"},
        404: {"description": "Parent event not found"},
        403: {"description": "Event creator user mismatch with current user"},
    },
)
def add_market_to_event(
    market: MarketCreate, session: SessionDep, access_token: OAuth2Dep
):
    try:
        user_id = token.get_id_from_token(access_token)
        event_service.add_market(market, session, user_id)
    except InvalidTokenException:
        raise http_unauthorized_exception("Token is invalid")
    except NotFoundException:
        raise http_not_found_exception(message="Parent event was not found")
    except ForbiddenOperationException:
        raise http_forbidden_exception(
            message="Event creator user mismatch with current user"
        )


@router.get("/events", responses={401: {"description": "Invalid token"}})
def get_today_events(
    session: SessionDep,
    access_token: OAuth2Dep,
    day_offset: int = 0,
    timezone: TimeZoneName = TimeZoneName("UTC"),
) -> list[EventPublic]:
    try:
        user_id = token.get_id_from_token(access_token)
        events = event_service.get_today_events(
            session=session, user_id=user_id, timezone=timezone, day_offset=day_offset
        )
    except InvalidTokenException:
        raise http_unauthorized_exception("Token is invalid")
    # TimezoneValidationException is alredy handled by pydantic validation for TimeZoneName

    return events


@router.post(
    "/refund",
    responses={
        401: {"description": "Invalid token"},
        404: {"description": "The event was not found"},
        403: {
            "description": "Bad request",
            "content": {
                "application/json": {
                    "examples": {
                        "event_not_ended": {
                            "summary": "The event has not ended yet",
                            "value": {
                                "detail": "You are trying to refund bets on an event that has not ended yet"
                            },
                        },
                        "user_not_creator": {
                            "summary": "The current user is not the event creator",
                            "value": {
                                "detail": "You are trying to refund bets on an event that you did not create"
                            },
                        },
                    }
                }
            },
        },
    },
)
def refund_event(session: SessionDep, access_token: OAuth2Dep, event_id: int):
    try:
        user_id = token.get_id_from_token(access_token)
        event_service.refund_event(session=session, user_id=user_id, event_id=event_id)
    except InvalidTokenException:
        raise http_unauthorized_exception("Token is invalid")
    except NotFoundException as e:
        raise http_not_found_exception(e.args[0])
    except ForbiddenOperationException as e:
        raise http_forbidden_exception(e.args[0])
