from fastapi import APIRouter, Query

from auth import token
from auth.security_schema import OAuth2Dep
from globals.database import SessionDep
from globals.exceptions import InvalidTokenException, http_unauthorized_exception
from models import TransactionPublic
from service import transaction_service

router = APIRouter()


@router.get(
    "/transactions",
    summary="Get transaction history",
    description="Retrieve the transaction history for the currently authenticated user, including bets, refunds, and winnings. Supports pagination.",
    responses={401: {"description": "Invalid token"}},
    openapi_extra={
        "x-code-samples": [
            {
                "lang": "cURL",
                "label": "cURL",
                "source": "curl -X GET \"https://api.example.com/transactions?limit=20&page=0\" \\\n     -H \"X-CHAOS-Auth: <your_token>\"",
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": "import requests\n\nurl = \"https://api.example.com/transactions\"\nheaders = {\"X-CHAOS-Auth\": \"<your_token>\"}\nparams = {\"limit\": 20, \"page\": 0}\n\nresponse = requests.get(url, headers=headers, params=params)\nprint(response.json())",
            },
            {
                "lang": "Dart",
                "label": "Dart (Dio)",
                "source": "import 'package:dio/dio.dart';\n\nvoid getTransactions() async {\n  var dio = Dio();\n  var response = await dio.get('https://api.example.com/transactions', \n    queryParameters: {'limit': 20, 'page': 0},\n    options: Options(headers: {'X-CHAOS-Auth': '<your_token>'}),\n  );\n  print(response.data);\n}",
            },
        ]
    },
)
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
