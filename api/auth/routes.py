from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from globals.database import SessionDep
from globals.exceptions import http_unauthorized_exception

from auth.auth_user import authenticate_user
from auth.token import create_access_token

router = APIRouter()


@router.post(
    "/token",
    summary="Login for access token",
    description="Authenticate with username and password to receive a JWT access token. If the API is behind the Nginx proxy, this token must be sent using the `X-CHAOS-Auth` header in subsequent requests.",
    responses={
        200: {
            "description": "Successful Login. The JWT payload contains the field `sub` with the user ID in the format `user:id`.",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                    }
                }
            },
        },
        401: {"description": "Incorrect username or password"},
    },
    openapi_extra={
        "x-code-samples": [
            {
                "lang": "cURL",
                "label": "cURL",
                "source": "curl -X POST \"https://api.example.com/token\" \\\n     -H \"Content-Type: application/x-www-form-urlencoded\" \\\n     -d \"username=john_doe&password=secure_password\"",
            },
            {
                "lang": "Python",
                "label": "Python (requests)",
                "source": "import requests\n\nurl = \"https://api.example.com/token\"\ndata = {\n    \"username\": \"john_doe\",\n    \"password\": \"secure_password\"\n}\n\nresponse = requests.post(url, data=data)\nprint(response.json())",
            },
            {
                "lang": "Dart",
                "label": "Dart (Dio)",
                "source": "import 'package:dio/dio.dart';\n\nvoid login() async {\n  var dio = Dio();\n  var formData = FormData.fromMap({\n    'username': 'john_doe',\n    'password': 'secure_password',\n  });\n\n  var response = await dio.post('https://api.example.com/token', data: formData);\n  print(response.data);\n}",
            },
        ]
    },
)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
):
    user = authenticate_user(session, form_data.username, form_data.password)

    if not user:
        raise http_unauthorized_exception("Incorrect username or password")

    payload = {"sub": f"user:{user.id}"}
    token = create_access_token(payload)

    return token
