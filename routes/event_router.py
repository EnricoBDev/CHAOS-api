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

    return events
