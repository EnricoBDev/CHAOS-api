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
    summary="Place a new bet",
    description="Place a bet on a specific outcome of an event. Validates user balance, event status, and ensures the user is not the event creator.",
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
    openapi_extra={
        "x-code-samples": [
            {
                "lang": "cURL",
                "label": "cURL",
                "source": "curl -X POST \"https://api.example.com/bet\" \\\n     -H \"Content-Type: application/json\" \\\n     -H \"X-CHAOS-Auth: <your_token>\" \\\n     -d '{\"outcome_id\": 1, \"amount\": 100}'",
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": "import requests\n\nurl = \"https://api.example.com/bet\"\nheaders = {\"X-CHAOS-Auth\": \"<your_token>\"}\npayload = {\"outcome_id\": 1, \"amount\": 100}\n\nresponse = requests.post(url, headers=headers, json=payload)\nprint(response.status_code)",
            },
            {
                "lang": "Dart",
                "label": "Dart (Dio)",
                "source": "import 'package:dio/dio.dart';\n\nvoid placeBet() async {\n  var dio = Dio();\n  var payload = {'outcome_id': 1, 'amount': 100};\n\n  var response = await dio.post('https://api.example.com/bet', \n    data: payload,\n    options: Options(headers: {'X-CHAOS-Auth': '<your_token>'}),\n  );\n  print(response.statusCode);\n}",
            },
        ]
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
    summary="Delete a bet",
    description="Remove an existing bet. Only allowed if the bet exists and belongs to the current user, and the event hasn't started yet.",
    responses={
        401: {"description": "Invalid token"},
        404: {"description": "Bet not found"},
        403: {"description": "Bad request"},
    },
    openapi_extra={
        "x-code-samples": [
            {
                "lang": "cURL",
                "label": "cURL",
                "source": "curl -X DELETE \"https://api.example.com/bet?bet_id=1\" \\\n     -H \"X-CHAOS-Auth: <your_token>\"",
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": "import requests\n\nurl = \"https://api.example.com/bet\"\nheaders = {\"X-CHAOS-Auth\": \"<your_token>\"}\nparams = {\"bet_id\": 1}\n\nresponse = requests.delete(url, headers=headers, params=params)\nprint(response.status_code)",
            },
            {
                "lang": "Dart",
                "label": "Dart (Dio)",
                "source": "import 'package:dio/dio.dart';\n\nvoid deleteBet() async {\n  var dio = Dio();\n  var response = await dio.delete('https://api.example.com/bet', \n    queryParameters: {'bet_id': 1},\n    options: Options(headers: {'X-CHAOS-Auth': '<your_token>'}),\n  );\n  print(response.statusCode);\n}",
            },
        ]
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
