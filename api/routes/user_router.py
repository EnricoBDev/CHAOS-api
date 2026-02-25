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
    responses={
        409: {"description": "UNIQUE constraint violated on email and/or username"}
    },
)
def create_user(user: UserCreate, session: SessionDep):
    try:
        user_service.create_new_user(user, session)
    except UniqueViolationException:
        raise http_conflict_exception(
            "A user with the same username and/or password already exists"
        )


@router.get("/me", responses={401: {"description": "Invalid token"}})
def get_current_user(session: SessionDep, access_token: OAuth2Dep) -> UserPublic:
    try:
        user = user_service.get_current_user(session, access_token)
    except InvalidTokenException:
        raise http_unauthorized_exception("Token is invalid")

    return user  # ty:ignore[invalid-return-type]
