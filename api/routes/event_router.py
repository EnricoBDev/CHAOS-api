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


@router.post(
    "/event",
    summary="Create a new event",
    description="Create a new betting event. The current user will be designated as the creator.",
    responses={401: {"description": "Invalid token"}},
    openapi_extra={
        "x-code-samples": [
            {
                "lang": "cURL",
                "label": "cURL",
                "source": "curl -X POST \"https://api.example.com/event\" \\\n     -H \"Content-Type: application/json\" \\\n     -H \"X-CHAOS-Auth: <your_token>\" \\\n     -d '{\"name\": \"Team A vs Team B\", \"event_date\": \"2026-03-23T20:00:00Z\", \"category\": \"Soccer\"}'",
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": "import requests\n\nurl = \"https://api.example.com/event\"\nheaders = {\"X-CHAOS-Auth\": \"<your_token>\"}\npayload = {\n    \"name\": \"Team A vs Team B\",\n    \"event_date\": \"2026-03-23T20:00:00Z\",\n    \"category\": \"Soccer\"\n}\n\nresponse = requests.post(url, headers=headers, json=payload)\nprint(response.status_code)",
            },
            {
                "lang": "Dart",
                "label": "Dart (Dio)",
                "source": "import 'package:dio/dio.dart';\n\nvoid createEvent() async {\n  var dio = Dio();\n  var payload = {\n    'name': 'Team A vs Team B',\n    'event_date': '2026-03-23T20:00:00Z',\n    'category': 'Soccer'\n  };\n\n  var response = await dio.post('https://api.example.com/event', \n    data: payload,\n    options: Options(headers: {'X-CHAOS-Auth': '<your_token>'}),\n  );\n  print(response.statusCode);\n}",
            },
        ]
    },
)
def create_new_event(event: EventCreate, session: SessionDep, access_token: OAuth2Dep):
    try:
        user_id = token.get_id_from_token(access_token)
        event_service.create_event(event, session, user_id)
    except InvalidTokenException:
        raise http_unauthorized_exception("Token is invalid")


@router.post(
    "/market",
    summary="Add market to event",
    description="Add a new betting market to an existing event. Only the event creator can add markets.",
    responses={
        401: {"description": "Invalid token"},
        404: {"description": "Parent event not found"},
        403: {"description": "Event creator user mismatch with current user"},
    },
    openapi_extra={
        "x-code-samples": [
            {
                "lang": "cURL",
                "label": "cURL",
                "source": "curl -X POST \"https://api.example.com/market\" \\\n     -H \"Content-Type: application/json\" \\\n     -H \"X-CHAOS-Auth: <your_token>\" \\\n     -d '{\"event_id\": 1, \"name\": \"Winner\", \"outcomes\": [{\"name\": \"Team A\", \"odds\": 1.5}, {\"name\": \"Team B\", \"odds\": 2.5}]}'",
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": "import requests\n\nurl = \"https://api.example.com/market\"\nheaders = {\"X-CHAOS-Auth\": \"<your_token>\"}\npayload = {\n    \"event_id\": 1,\n    \"name\": \"Winner\",\n    \"outcomes\": [\n        {\"name\": \"Team A\", \"odds\": 1.5},\n        {\"name\": \"Team B\", \"odds\": 2.5}\n    ]\n}\n\nresponse = requests.post(url, headers=headers, json=payload)\nprint(response.status_code)",
            },
            {
                "lang": "Dart",
                "label": "Dart (Dio)",
                "source": "import 'package:dio/dio.dart';\n\nvoid addMarket() async {\n  var dio = Dio();\n  var payload = {\n    'event_id': 1,\n    'name': 'Winner',\n    'outcomes': [\n      {'name': 'Team A', 'odds': 1.5},\n      {'name': 'Team B', 'odds': 2.5}\n    ]\n  };\n\n  var response = await dio.post('https://api.example.com/market', \n    data: payload,\n    options: Options(headers: {'X-CHAOS-Auth': '<your_token>'}),\n  );\n  print(response.statusCode);\n}",
            },
        ]
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


@router.get(
    "/events",
    summary="Get events for a specific day",
    description="Retrieve a list of events for a given day offset and timezone.",
    responses={401: {"description": "Invalid token"}},
    openapi_extra={
        "x-code-samples": [
            {
                "lang": "cURL",
                "label": "cURL",
                "source": "curl -X GET \"https://api.example.com/events?day_offset=0&timezone=Europe/Rome\" \\\n     -H \"X-CHAOS-Auth: <your_token>\"",
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": "import requests\n\nurl = \"https://api.example.com/events\"\nheaders = {\"X-CHAOS-Auth\": \"<your_token>\"}\nparams = {\"day_offset\": 0, \"timezone\": \"Europe/Rome\"}\n\nresponse = requests.get(url, headers=headers, params=params)\nprint(response.json())",
            },
            {
                "lang": "Dart",
                "label": "Dart (Dio)",
                "source": "import 'package:dio/dio.dart';\n\nvoid getEvents() async {\n  var dio = Dio();\n  var response = await dio.get('https://api.example.com/events', \n    queryParameters: {'day_offset': 0, 'timezone': 'Europe/Rome'},\n    options: Options(headers: {'X-CHAOS-Auth': '<your_token>'}),\n  );\n  print(response.data);\n}",
            },
        ]
    },
)
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
    summary="Refund an event",
    description="Refund all bets placed on an event. Only the event creator can perform this action, and only after the event has ended.",
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
                            "value": {"detail": "The event is not over yet"},
                        },
                        "user_not_creator": {
                            "summary": "The current user is not the event creator",
                            "value": {"detail": "You are not the event creator"},
                        },
                    }
                }
            },
        },
    },
    openapi_extra={
        "x-code-samples": [
            {
                "lang": "cURL",
                "label": "cURL",
                "source": "curl -X POST \"https://api.example.com/refund?event_id=1\" \\\n     -H \"X-CHAOS-Auth: <your_token>\"",
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": "import requests\n\nurl = \"https://api.example.com/refund\"\nheaders = {\"X-CHAOS-Auth\": \"<your_token>\"}\nparams = {\"event_id\": 1}\n\nresponse = requests.post(url, headers=headers, params=params)\nprint(response.status_code)",
            },
            {
                "lang": "Dart",
                "label": "Dart (Dio)",
                "source": "import 'package:dio/dio.dart';\n\nvoid refundEvent() async {\n  var dio = Dio();\n  var response = await dio.post('https://api.example.com/refund', \n    queryParameters: {'event_id': 1},\n    options: Options(headers: {'X-CHAOS-Auth': '<your_token>'}),\n  );\n  print(response.statusCode);\n}",
            },
        ]
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
