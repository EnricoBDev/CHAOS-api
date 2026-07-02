from fastapi import APIRouter

from auth.security_schema import OAuth2Dep
from globals.database import SessionDep
from globals.exceptions import (
    InvalidTokenException,
    UniqueViolationException,
    http_conflict_exception,
    http_unauthorized_exception,
)
from models import UserCreate, UserPublic
from service import user_service

router = APIRouter()


@router.post(
    "/user",
    summary="Create a new user",
    description="Register a new user in the system with a unique username and email.",
    responses={
        409: {"description": "UNIQUE constraint violated on email and/or username"}
    },
    openapi_extra={
        "x-code-samples": [
            {
                "lang": "cURL",
                "label": "cURL",
                "source": "curl -X POST \"https://api.example.com/user\" \\\n     -H \"Content-Type: application/json\" \\\n     -d '{\"username\": \"john_doe\", \"email\": \"john@example.com\", \"password\": \"secure_password\"}'",
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": "import requests\n\nurl = \"https://api.example.com/user\"\npayload = {\n    \"username\": \"john_doe\",\n    \"email\": \"john@example.com\",\n    \"password\": \"secure_password\"\n}\n\nresponse = requests.post(url, json=payload)\nprint(response.status_code)",
            },
            {
                "lang": "Dart",
                "label": "Dart (Dio)",
                "source": "import 'package:dio/dio.dart';\n\nvoid createUser() async {\n  var dio = Dio();\n  var payload = {\n    'username': 'john_doe',\n    'email': 'john@example.com',\n    'password': 'secure_password',\n  };\n\n  var response = await dio.post('https://api.example.com/user', data: payload);\n  print(response.statusCode);\n}",
            },
        ]
    },
)
def create_user(user: UserCreate, session: SessionDep):
    try:
        user_service.create_new_user(user, session)
    except UniqueViolationException:
        raise http_conflict_exception(
            "A user with the same username and/or password already exists"
        )


@router.get(
    "/me",
    summary="Get current user profile",
    description="Retrieve the profile information of the currently authenticated user.",
    responses={401: {"description": "Invalid token"}},
    openapi_extra={
        "x-code-samples": [
            {
                "lang": "cURL",
                "label": "cURL",
                "source": "curl -X GET \"https://api.example.com/me\" \\\n     -H \"X-CHAOS-Auth: <your_token>\"",
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": "import requests\n\nurl = \"https://api.example.com/me\"\n# Note: Use 'Authorization' for direct API or 'X-CHAOS-Auth' for proxy\nheaders = {\"X-CHAOS-Auth\": \"<your_token>\"}\n\nresponse = requests.get(url, headers=headers)\nprint(response.json())",
            },
            {
                "lang": "Dart",
                "label": "Dart (Dio)",
                "source": "import 'package:dio/dio.dart';\n\nvoid getMe() async {\n  var dio = Dio();\n  // Note: Use 'Authorization' for direct API or 'X-CHAOS-Auth' for proxy\n  var response = await dio.get('https://api.example.com/me', \n    options: Options(headers: {'X-CHAOS-Auth': '<your_token>'}),\n  );\n  print(response.data);\n}",
            },
        ]
    },
)
def get_current_user(session: SessionDep, access_token: OAuth2Dep) -> UserPublic:
    try:
        user = user_service.get_current_user(session, access_token)
    except InvalidTokenException:
        raise http_unauthorized_exception("Token is invalid")

    return user  # ty:ignore[invalid-return-type]
