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
    summary="Select winning outcomes",
    description="Select the winning outcomes for a finished event and settle all associated bets. Only the event creator can perform this action.",
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
    openapi_extra={
        "x-code-samples": [
            {
                "lang": "cURL",
                "label": "cURL",
                "source": "curl -X POST \"https://api.example.com/winning-outcome\" \\\n     -H \"Content-Type: application/json\" \\\n     -H \"X-CHAOS-Auth: <your_token>\" \\\n     -d '[1, 5, 12]'",
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": "import requests\n\nurl = \"https://api.example.com/winning-outcome\"\nheaders = {\"X-CHAOS-Auth\": \"<your_token>\"}\npayload = [1, 5, 12]\n\nresponse = requests.post(url, headers=headers, json=payload)\nprint(response.status_code)",
            },
            {
                "lang": "Dart",
                "label": "Dart (Dio)",
                "source": "import 'package:dio/dio.dart';\n\nvoid selectWinningOutcomes() async {\n  var dio = Dio();\n  var payload = [1, 5, 12];\n\n  var response = await dio.post('https://api.example.com/winning-outcome', \n    data: payload,\n    options: Options(headers: {'X-CHAOS-Auth': '<your_token>'}),\n  );\n  print(response.statusCode);\n}",
            },
        ]
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
