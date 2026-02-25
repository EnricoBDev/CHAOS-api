from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from auth.auth_user import authenticate_user
from auth.token import create_access_token
from globals.database import SessionDep
from globals.exceptions import http_unauthorized_exception

router = APIRouter()


@router.post(
    "/token", responses={401: {"description": "Incorrect username or password"}}
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
