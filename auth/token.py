import jwt
from jwt import InvalidTokenError
from pydantic import BaseModel

from globals.constants import ALGORITHM, JWT_EXP, NOT_SO_SECRET
from globals.exceptions import InvalidTokenException


class Token(BaseModel):
    access_token: str
    token_type: str


def create_access_token(data: dict) -> Token:
    to_encode = data.copy()
    to_encode.update({"exp": JWT_EXP})
    encoded_jwt = jwt.encode(to_encode, NOT_SO_SECRET, algorithm=ALGORITHM)
    return Token(access_token=encoded_jwt, token_type="bearer")


def get_id_from_token(token: str) -> int:
    try:
        payload: dict = jwt.decode(token, NOT_SO_SECRET, algorithms=[ALGORITHM])
    except InvalidTokenError:
        raise InvalidTokenException()

    if payload.get("sub") is None:
        raise InvalidTokenException()

    id: int = int(payload.get("sub").split(":")[1])

    return id
